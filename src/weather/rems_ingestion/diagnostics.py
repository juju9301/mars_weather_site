import csv
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

from .pds import (
    RemsDataError,
    _find_product_file,
    _read_table,
    _select_table,
    _table_definitions,
)


_REQUIRED_COLUMNS = {
    "RMD": {"LTST", "AMBIENT_TEMP", "BRIGHTNESS_TEMP", "PRESSURE"},
    "ADR": {"LTST", "SOLAR_ZENITHAL_ANGLE"},
}
_PRODUCTS = tuple(_REQUIRED_COLUMNS)
_ProductSummary = dict[str, Any]


def _row_sol(row: dict[str, str], product: str, row_number: int) -> tuple[str, int]:
    value = row.get("LTST", "").strip()
    prefix = value.split(maxsplit=1)
    if not prefix or len(prefix[0]) != 5 or not prefix[0].isdigit():
        raise RemsDataError(
            f"{product} PDS row {row_number} has invalid LTST {value!r}."
        )
    return prefix[0], int(prefix[0])


def stage_rems_products(
    data_root: Path,
    sols: list[int],
    staging_directory: Path,
    logger: logging.Logger,
) -> tuple[dict[int, dict[str, Path]], dict[int, dict[str, _ProductSummary]]]:
    """Diagnose per-sol products and stage rows by the sol recorded in LTST."""
    requested_sols = set(sols)
    source_sols = sorted(
        requested_sols | {sol - 1 for sol in requested_sols if sol > 0}
    )
    candidates: dict[tuple[int, str], list[tuple[int, dict[str, str]]]] = defaultdict(list)
    column_orders: dict[tuple[int, str], list[str]] = defaultdict(list)
    summaries: dict[int, dict[str, _ProductSummary]] = {
        sol: {
            product: {
                "rows_by_source_sol": {},
                "routed_in_rows": 0,
                "routed_out_rows": {},
                "unrouted_other_sol_rows": {},
                "duplicate_rows_removed": 0,
            }
            for product in _PRODUCTS
        }
        for sol in sols
    }

    for source_sol in source_sols:
        is_requested_source = source_sol in requested_sols
        for product in _PRODUCTS:
            xml_path = _find_product_file(data_root, source_sol, product, ".xml")
            table_path = _find_product_file(data_root, source_sol, product, ".TAB")
            if xml_path is None or table_path is None:
                if is_requested_source:
                    missing_suffix = ".xml" if xml_path is None else ".TAB"
                    raise RemsDataError(
                        f"Expected {product} {missing_suffix} file for sol "
                        f"{source_sol} under {data_root}; found 0."
                    )
                if xml_path is not None or table_path is not None:
                    logger.warning(
                        "Skipping optional predecessor product %s for sol %05d: "
                        "its XML label or table file is missing.",
                        product,
                        source_sol,
                    )
                continue

            columns, expected_rows = _select_table(
                _table_definitions(xml_path),
                _REQUIRED_COLUMNS[product],
                product,
            )
            rows = _read_table(table_path, columns, expected_rows)
            rows_by_sol: dict[str, int] = {}
            for row_number, row in enumerate(rows, start=1):
                sol_prefix, row_sol = _row_sol(row, product, row_number)
                rows_by_sol[sol_prefix] = rows_by_sol.get(sol_prefix, 0) + 1
                if row_sol not in requested_sols:
                    if row_sol != source_sol:
                        source_summary = summaries.get(source_sol)
                        if source_summary is not None:
                            excluded = source_summary[product][
                                "unrouted_other_sol_rows"
                            ]
                            excluded[sol_prefix] = excluded.get(sol_prefix, 0) + 1
                    continue

                key = (row_sol, product)
                candidates[key].append((source_sol, row))
                for column in columns:
                    if column not in column_orders[key]:
                        column_orders[key].append(column)
                target_summary = summaries[row_sol][product]
                source_counts = target_summary["rows_by_source_sol"]
                source_key = f"{source_sol:05d}"
                source_counts[source_key] = source_counts.get(source_key, 0) + 1
                if source_sol != row_sol:
                    target_summary["routed_in_rows"] += 1
                    source_summary = summaries.get(source_sol)
                    if source_summary is not None:
                        routed_out = source_summary[product]["routed_out_rows"]
                        routed_out[sol_prefix] = routed_out.get(sol_prefix, 0) + 1

            logger.info(
                "Diagnosed %s sol %05d: %d rows; LTST sols: %s",
                product,
                source_sol,
                len(rows),
                ", ".join(
                    f"{prefix}={count}"
                    for prefix, count in sorted(rows_by_sol.items())
                ),
            )
            for prefix, count in sorted(rows_by_sol.items()):
                if int(prefix) != source_sol and int(prefix) in requested_sols:
                    logger.warning(
                        "Spillover found: %s product for sol %05d contains %d "
                        "rows for sol %s; staging them for sol %s.",
                        product,
                        source_sol,
                        count,
                        prefix,
                        prefix,
                    )

    staged_paths: dict[int, dict[str, Path]] = {sol: {} for sol in sols}
    for sol in sols:
        for product in _PRODUCTS:
            key = (sol, product)
            product_candidates = candidates.get(key, [])
            if not product_candidates:
                raise RemsDataError(
                    f"No {product} rows found for requested sol {sol:05d}."
                )

            product_candidates.sort(
                key=lambda item: (item[0] != sol, item[0])
            )
            retained_rows = []
            seen_timestamp_sources: dict[str, int] = {}
            duplicates_removed = 0
            for source_sol, row in product_candidates:
                timestamp = row.get("TIMESTAMP", "").strip()
                previous_source = seen_timestamp_sources.get(timestamp)
                if timestamp and previous_source is not None and previous_source != source_sol:
                    duplicates_removed += 1
                    continue
                if timestamp:
                    seen_timestamp_sources[timestamp] = source_sol
                retained_rows.append(row)

            retained_rows.sort(key=lambda row: row["LTST"].strip())
            output_columns = column_orders[key]
            staged_path = staging_directory / f"sol_{sol:05d}_{product}.csv"
            try:
                with staged_path.open(
                    "w", encoding="ascii", newline=""
                ) as output:
                    writer = csv.DictWriter(
                        output,
                        fieldnames=output_columns,
                        extrasaction="ignore",
                        lineterminator="\n",
                    )
                    writer.writeheader()
                    writer.writerows(retained_rows)
            except (OSError, csv.Error, UnicodeError) as exc:
                raise RemsDataError(
                    f"Could not write staged {product} rows for sol {sol}: {exc}"
                ) from exc

            summary = summaries[sol][product]
            summary["duplicate_rows_removed"] = duplicates_removed
            staged_paths[sol][product] = staged_path
            logger.info(
                "Staged sol %05d %s: %d rows from %s; %d duplicate "
                "cross-file timestamps removed.",
                sol,
                product,
                len(retained_rows),
                ", ".join(sorted(summary["rows_by_source_sol"])),
                duplicates_removed,
            )

    return staged_paths, summaries
