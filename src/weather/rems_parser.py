import csv
import json
import math
import re
import statistics
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from typing import Any


class RemsDataError(ValueError):
    pass


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _product_file(data_root: Path, sol: int, product: str, suffix: str) -> Path:
    matches = list(data_root.glob(f"{sol}/*{product}{sol:04d}*{suffix}"))
    if not matches and suffix == ".LBL":
        matches = list(data_root.glob(f"{sol}/*{product}{sol:04d}*.LBL.txt"))
    if len(matches) != 1:
        raise RemsDataError(
            f"Expected exactly one {product} {suffix} file for sol {sol} "
            f"under {data_root}; found {len(matches)}."
        )
    return matches[0]


def _label_value(label_path: Path, key: str) -> str:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*=\s*(.*?)\s*$")
    for line in label_path.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1).strip().strip('"')
    raise RemsDataError(f"Missing {key} in PDS label {label_path}.")


def _parse_terrestrial_date(value: str) -> date:
    match = re.match(r"^(\d{4})[-:](\d{2})[-:\s]\s*(\d{2})T", value)
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


def _valid_measurements(
    rows: list[dict[str, str]], column: str
) -> list[float]:
    values = [
        value
        for index, row in enumerate(rows, start=1)
        if (value := _measurement(row, column, index)) is not None
    ]
    if not values:
        raise RemsDataError(f"No valid measurements found for {column}.")
    return values


def _celsius(value_kelvin: float) -> int:
    return round(value_kelvin - 273.15)


def _wind_direction(rows: list[dict[str, str]]) -> str | None:
    directions = []
    for index, row in enumerate(rows, start=1):
        direction = _measurement(row, "WIND_DIRECTION", index)
        if direction is not None:
            directions.append(math.radians(direction))
    if not directions:
        return None

    east = sum(math.sin(direction) for direction in directions)
    north = sum(math.cos(direction) for direction in directions)
    if math.isclose(east, 0.0, abs_tol=1e-12) and math.isclose(
        north, 0.0, abs_tol=1e-12
    ):
        return None
    degrees = math.degrees(math.atan2(east, north)) % 360
    if math.isclose(degrees, 360.0, abs_tol=1e-10):
        degrees = 0.0
    return f"{degrees:.2f}"


def _ltst_seconds(value: str) -> float:
    try:
        hours, minutes, seconds = value.strip().split()[-1].split(":")
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except (IndexError, ValueError) as exc:
        raise RemsDataError(f"Invalid LTST value: {value!r}.") from exc


def _validate_ltst_sol(rows: list[dict[str, str]], sol: int, product: str) -> None:
    expected_sol = f"{sol:05d}"
    for row_number, row in enumerate(rows, start=1):
        prefix = row["LTST"].strip().split(maxsplit=1)
        if not prefix or prefix[0] != expected_sol:
            value = row["LTST"].strip()
            raise RemsDataError(
                f"{product} PDS row {row_number} has LTST {value!r}; "
                f"expected sol {expected_sol}."
            )


def _format_solar_crossing(
    rows: list[dict[str, str]], *, sunrise: bool
) -> str:
    points = []
    for index, row in enumerate(rows, start=1):
        zenith = _measurement(row, "SOLAR_ZENITHAL_ANGLE", index)
        if zenith is not None:
            points.append((_ltst_seconds(row["LTST"]), zenith))

    for (time_before, angle_before), (time_after, angle_after) in zip(
        points, points[1:]
    ):
        if sunrise:
            crossing = angle_before > 90 >= angle_after
        else:
            crossing = angle_before <= 90 < angle_after
        if not crossing:
            continue

        fraction = (90 - angle_before) / (angle_after - angle_before)
        crossing_seconds = time_before + fraction * (time_after - time_before)
        total_minutes = round(crossing_seconds / 60) % (24 * 60)
        return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"

    name = "sunrise" if sunrise else "sunset"
    raise RemsDataError(f"Could not determine {name} from the ADR solar geometry.")


def parse_weather_record(data_root: Path, sol: int) -> dict[str, Any]:
    """Parse one REMS sol into a Django fixture record."""
    data_root = Path(data_root)
    rmd_label = _product_file(data_root, sol, "RMD", ".LBL")
    rmd_xml = _product_file(data_root, sol, "RMD", ".xml")
    rmd_table = _product_file(data_root, sol, "RMD", ".TAB")
    adr_xml = _product_file(data_root, sol, "ADR", ".xml")
    adr_table = _product_file(data_root, sol, "ADR", ".TAB")

    try:
        label_sol = int(_label_value(rmd_label, "PLANET_DAY_NUMBER"))
    except ValueError as exc:
        raise RemsDataError(
            f"Invalid PLANET_DAY_NUMBER in PDS label {rmd_label}."
        ) from exc
    if label_sol != sol:
        raise RemsDataError(
            f"Requested sol {sol}, but {rmd_label} describes sol {label_sol}."
        )
    terrestrial_date = _parse_terrestrial_date(
        _label_value(rmd_label, "STOP_TIME")
    )

    rmd_columns, rmd_count = _select_table(
        _table_definitions(rmd_xml),
        {
            "AMBIENT_TEMP",
            "BRIGHTNESS_TEMP",
            "PRESSURE",
            "HORIZONTAL_WIND_SPEED",
            "WIND_DIRECTION",
        },
        "RMD",
    )
    rmd_rows = _read_table(rmd_table, rmd_columns, rmd_count)
    _validate_ltst_sol(rmd_rows, sol, "RMD")
    adr_columns, adr_count = _select_table(
        _table_definitions(adr_xml),
        {"LTST", "SOLAR_ZENITHAL_ANGLE"},
        "ADR",
    )
    adr_rows = _read_table(adr_table, adr_columns, adr_count)
    _validate_ltst_sol(adr_rows, sol, "ADR")

    ambient_temps = _valid_measurements(rmd_rows, "AMBIENT_TEMP")
    gts_temps = _valid_measurements(rmd_rows, "BRIGHTNESS_TEMP")
    pressures = _valid_measurements(rmd_rows, "PRESSURE")
    wind_speeds = [
        value
        for index, row in enumerate(rmd_rows, start=1)
        if (value := _measurement(row, "HORIZONTAL_WIND_SPEED", index))
        is not None
    ]

    fields = {
        "orig_id": None,
        "terrestrial_date": terrestrial_date.isoformat(),
        "sol": sol,
        "ls": None,
        "season": None,
        "min_temp": _celsius(min(ambient_temps)),
        "max_temp": _celsius(max(ambient_temps)),
        "pressure": round(statistics.mean(pressures)),
        "pressure_string": None,
        "abs_humidity": None,
        "wind_speed": (
            f"{statistics.mean(wind_speeds):.2f}" if wind_speeds else None
        ),
        "wind_direction": _wind_direction(rmd_rows),
        "atmo_opacity": None,
        "sunrise": _format_solar_crossing(adr_rows, sunrise=True),
        "sunset": _format_solar_crossing(adr_rows, sunrise=False),
        "local_uv_irradiance_index": None,
        "min_gts_temp": _celsius(min(gts_temps)),
        "max_gts_temp": _celsius(max(gts_temps)),
        "source": "NASA PDS REMS RDR",
    }
    return {"model": "weather.Weather", "fields": fields}


def fixture_json(record: dict[str, Any]) -> str:
    return json.dumps([record], indent=2, ensure_ascii=False) + "\n"
