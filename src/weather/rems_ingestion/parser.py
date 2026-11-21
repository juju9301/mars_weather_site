from pathlib import Path
from typing import Any

from .calculations import summarize_weather
from .pds import (
    RemsDataError,
    _label_value,
    _parse_terrestrial_date,
    _product_file,
    _read_table,
    _select_table,
    _table_definitions,
    _validate_ltst_sol,
)


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
            "LTST",
            "AMBIENT_TEMP",
            "BRIGHTNESS_TEMP",
            "PRESSURE",
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

    summary_fields, quality_summary = summarize_weather(rmd_rows, adr_rows)
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
