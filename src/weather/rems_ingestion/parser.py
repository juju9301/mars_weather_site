import logging
import tempfile
from pathlib import Path
from typing import Any

from .calculations import summarize_weather
from .diagnostics import stage_rems_products
from .pds import (
    RemsDataError,
    _label_value,
    _parse_terrestrial_date,
    _product_file,
    _read_staged_table,
    _select_table,
    _table_definitions,
)


def _parse_weather_record(
    data_root: Path,
    sol: int,
    staged_products: dict[str, Path],
    staging_summary: dict[str, dict[str, object]],
) -> dict[str, Any]:
    data_root = Path(data_root)
    rmd_label = _product_file(data_root, sol, "RMD", ".LBL")
    rmd_xml = _product_file(data_root, sol, "RMD", ".xml")
    adr_xml = _product_file(data_root, sol, "ADR", ".xml")

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

    rmd_columns, _ = _select_table(
        _table_definitions(rmd_xml),
        {
            "LTST",
            "AMBIENT_TEMP",
            "BRIGHTNESS_TEMP",
            "PRESSURE",
        },
        "RMD",
    )
    rmd_rows = _read_staged_table(staged_products["RMD"])
    if not set(rmd_columns).issubset(rmd_rows[0]):
        raise RemsDataError(
            f"Staged RMD data for sol {sol} is missing columns from its PDS label."
        )
    adr_columns, _ = _select_table(
        _table_definitions(adr_xml),
        {"LTST", "SOLAR_ZENITHAL_ANGLE"},
        "ADR",
    )
    adr_rows = _read_staged_table(staged_products["ADR"])
    if not set(adr_columns).issubset(adr_rows[0]):
        raise RemsDataError(
            f"Staged ADR data for sol {sol} is missing columns from its PDS label."
        )

    summary_fields, quality_summary = summarize_weather(rmd_rows, adr_rows)
    quality_summary["excluded_other_sol_rows"] = {
        product.lower(): staging_summary[product]["unrouted_other_sol_rows"]
        for product in ("RMD", "ADR")
    }
    quality_summary["product_staging"] = staging_summary
    fields: dict[str, Any] = {
        "orig_id": None,
        "terrestrial_date": terrestrial_date.isoformat(),
        "sol": sol,
        "ls": None,
        "season": None,
        "pressure_string": None,
        "local_uv_irradiance_index": None,
        "source": "NASA PDS REMS RDR",
        "rems_quality_summary": quality_summary,
        **summary_fields,
    }
    return {"model": "weather.Weather", "fields": fields}


def parse_weather_records(
    data_root: Path,
    sols: list[int],
    *,
    logger: logging.Logger | None = None,
) -> list[dict[str, Any]]:
    """Diagnose products, stage boundary rows, and parse the requested sols."""
    if not sols:
        raise RemsDataError("At least one sol must be requested.")
    if any(sol < 0 for sol in sols):
        raise RemsDataError("Sol numbers must be non-negative.")
    if len(set(sols)) != len(sols):
        raise RemsDataError("Sol numbers must be unique.")

    logger = logger or logging.getLogger(__name__)
    with tempfile.TemporaryDirectory(prefix="rems-staging-") as directory:
        staged_products, staging_summaries = stage_rems_products(
            Path(data_root), sols, Path(directory), logger
        )
        return [
            _parse_weather_record(
                Path(data_root),
                sol,
                staged_products[sol],
                staging_summaries[sol],
            )
            for sol in sols
        ]


def parse_weather_record(data_root: Path, sol: int) -> dict[str, Any]:
    """Parse one REMS sol into a Django fixture record."""
    return parse_weather_records(data_root, [sol])[0]
