import csv
import math
import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path


class RemsDataError(ValueError):
    pass


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _find_product_file(
    data_root: Path, sol: int, product: str, suffix: str
) -> Path | None:
    directories = (
        data_root / str(sol),
        data_root / f"SOL{sol:05d}",
        data_root / f"SOL{sol:04d}",
        data_root,
    )
    matches = set()
    for directory in directories:
        matches.update(directory.glob(f"*{product}{sol:04d}*{suffix}"))
    if not matches and suffix == ".LBL":
        for directory in directories:
            matches.update(directory.glob(f"*{product}{sol:04d}*.LBL.txt"))

    if len(matches) != 1:
        if not matches:
            return None
        raise RemsDataError(
            f"Expected exactly one {product} {suffix} file for sol {sol} "
            f"under {data_root}; found {len(matches)}."
        )
    return matches.pop()


def _product_file(data_root: Path, sol: int, product: str, suffix: str) -> Path:
    path = _find_product_file(data_root, sol, product, suffix)
    if path is None:
        raise RemsDataError(
            f"Expected exactly one {product} {suffix} file for sol {sol} "
            f"under {data_root}; found 0."
        )
    return path


def _label_value(label_path: Path, key: str) -> str:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*=\s*(.*?)\s*$")
    for line in label_path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1).strip().strip('"')
    raise RemsDataError(f"Missing {key} in PDS label {label_path}.")


def _parse_terrestrial_date(value: str) -> date:
    match = re.match(r"^(\d{4})[-:](\d{2})[-:\s](\d{2})T", value)
    if not match:
        raise RemsDataError(f"Unsupported PDS STOP_TIME value: {value!r}.")
    year, month, day = (int(part) for part in match.groups())
    try:
        return date(year, month, day)
    except ValueError as exc:
        raise RemsDataError(f"Invalid PDS STOP_TIME value: {value!r}.") from exc


def _table_definitions(xml_path: Path) -> list[tuple[list[str], int]]:
    try:
        root = ET.parse(xml_path).getroot()
    except ET.ParseError as exc:
        raise RemsDataError(f"Invalid PDS XML label {xml_path}: {exc}") from exc

    tables = []
    for table in root.iter():
        if _local_name(table.tag) != "Table_Character":
            continue
        columns = []
        for field in table.iter():
            if not _local_name(field.tag).startswith("Field_"):
                continue
            name = next(
                (
                    child.text.strip()
                    for child in field
                    if _local_name(child.tag) == "name" and child.text
                ),
                None,
            )
            if name:
                columns.append(name)
        record_value = next(
            (
                child.text
                for child in table
                if _local_name(child.tag) == "records" and child.text
            ),
            None,
        )
        try:
            records = int(record_value) if record_value is not None else None
        except ValueError as exc:
            raise RemsDataError(
                f"Invalid record count in PDS XML label {xml_path}: "
                f"{record_value!r}."
            ) from exc
        if columns and records is not None:
            tables.append((columns, records))
    return tables


def _read_table(
    table_path: Path, columns: list[str], expected_records: int
) -> list[dict[str, str]]:
    try:
        with table_path.open(encoding="ascii", newline="") as source:
            rows = list(csv.reader(source))
    except (OSError, csv.Error, UnicodeError) as exc:
        raise RemsDataError(f"Could not read PDS table {table_path}: {exc}") from exc

    rows = [row for row in rows if len(row) == len(columns)]
    if len(rows) != expected_records:
        raise RemsDataError(
            f"PDS table {table_path} has {len(rows)} matching rows; "
            f"its XML label declares {expected_records}."
        )
    return [dict(zip(columns, row)) for row in rows]


def _read_staged_table(table_path: Path) -> list[dict[str, str]]:
    try:
        with table_path.open(encoding="ascii", newline="") as source:
            return list(csv.DictReader(source))
    except (OSError, csv.Error, UnicodeError) as exc:
        raise RemsDataError(f"Could not read staged PDS table {table_path}: {exc}") from exc


def _select_table(
    tables: list[tuple[list[str], int]], required_columns: set[str], product: str
) -> tuple[list[str], int]:
    matches = [
        table for table in tables if required_columns.issubset(set(table[0]))
    ]
    if len(matches) != 1:
        raise RemsDataError(
            f"Expected one {product} table containing "
            f"{', '.join(sorted(required_columns))}; found {len(matches)}."
        )
    return matches[0]


def _measurement(row: dict[str, str], column: str, row_number: int) -> float | None:
    value = row[column].strip()
    if not value:
        return None
    try:
        measurement = float(value)
    except ValueError as exc:
        raise RemsDataError(
            f"Invalid {column} value in PDS row {row_number}: {value!r}."
        ) from exc
    if not math.isfinite(measurement):
        raise RemsDataError(
            f"Invalid {column} value in PDS row {row_number}: {value!r}."
        )
    if measurement == -999:
        return None
    return measurement


def _ltst_seconds(value: str) -> float:
    try:
        hours, minutes, seconds = value.strip().split()[-1].split(":")
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except (IndexError, ValueError) as exc:
        raise RemsDataError(f"Invalid LTST value: {value!r}.") from exc


def _filter_rows_for_sol(
    rows: list[dict[str, str]], sol: int, product: str
) -> tuple[list[dict[str, str]], dict[str, int]]:
    expected_sol = f"{sol:05d}"
    selected_rows = []
    excluded_sol_counts: dict[str, int] = {}
    for row_number, row in enumerate(rows, start=1):
        prefix = row["LTST"].strip().split(maxsplit=1)
        if not prefix or not re.fullmatch(r"\d{5}", prefix[0]):
            value = row["LTST"].strip()
            raise RemsDataError(
                f"{product} PDS row {row_number} has invalid LTST {value!r}."
            )
        if prefix[0] == expected_sol:
            selected_rows.append(row)
        else:
            excluded_sol_counts[prefix[0]] = (
                excluded_sol_counts.get(prefix[0], 0) + 1
            )

    if not selected_rows:
        raise RemsDataError(
            f"No {product} PDS rows found for sol {expected_sol}."
        )
    return selected_rows, excluded_sol_counts
