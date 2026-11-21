import statistics
from collections import Counter

from .pds import RemsDataError, _ltst_seconds, _measurement


_SECONDS_PER_SOL = 24 * 60 * 60
_BURST_GAP_SECONDS = 60
_MISSING_FLAG = "<missing>"


def _measurements(rows: list[dict[str, str]], column: str) -> list[float]:
    values = [
        value
        for index, row in enumerate(rows, start=1)
        if (value := _measurement(row, column, index)) is not None
    ]
    if not values:
        raise RemsDataError(f"No valid measurements found for {column}.")
    return values


def _confidence_counts(
    rows: list[dict[str, str]], column: str
) -> tuple[str | None, dict[str, int]]:
    if not rows or column not in rows[0]:
        return None, {}
    counts = Counter(
        row[column].strip() or _MISSING_FLAG
        for row in rows
    )
    return column, dict(sorted(counts.items()))


def _metric_quality(
    rows: list[dict[str, str]],
    valid_samples: int,
    confidence_column: str,
) -> dict[str, object]:
    flag_column, flag_counts = _confidence_counts(rows, confidence_column)
    return {
        "valid_samples": valid_samples,
        "total_samples": len(rows),
        "confidence_flag_column": flag_column,
        "confidence_flag_counts": flag_counts,
    }


def _solar_crossing_seconds(
    rows: list[dict[str, str]], *, sunrise: bool
) -> float:
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
        return time_before + fraction * (time_after - time_before)

    name = "sunrise" if sunrise else "sunset"
    raise RemsDataError(f"Could not determine {name} from the ADR solar geometry.")


def _format_ltst(seconds: float) -> str:
    total_minutes = round(seconds / 60) % (24 * 60)
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def _coldest_burst(
    rows: list[dict[str, str]], column: str
) -> tuple[float, int, int]:
    burst_means = []
    burst_values = []
    previous_seconds = None

    for row_number, row in enumerate(rows, start=1):
        current_seconds = _ltst_seconds(row["LTST"])
        if previous_seconds is not None:
            gap = (current_seconds - previous_seconds) % _SECONDS_PER_SOL
            if gap > _BURST_GAP_SECONDS:
                if burst_values:
                    burst_means.append(
                        (statistics.mean(burst_values), len(burst_values))
                    )
                burst_values = []

        value = _measurement(row, column, row_number)
        if value is not None:
            burst_values.append(value)
        previous_seconds = current_seconds

    if burst_values:
        burst_means.append((statistics.mean(burst_values), len(burst_values)))
    if not burst_means:
        raise RemsDataError(f"No valid measurements found for {column}.")
    coldest_mean, coldest_samples = min(burst_means, key=lambda burst: burst[0])
    return coldest_mean, coldest_samples, len(burst_means)


def _celsius(value_kelvin: float) -> float:
    return round(value_kelvin - 273.15, 2)


def summarize_weather(
    rmd_rows: list[dict[str, str]],
    adr_rows: list[dict[str, str]],
) -> tuple[dict[str, object], dict[str, object]]:
    ambient_temps = _measurements(rmd_rows, "AMBIENT_TEMP")
    gts_temps = _measurements(rmd_rows, "BRIGHTNESS_TEMP")
    pressures = _measurements(rmd_rows, "PRESSURE")

    sunrise_seconds = _solar_crossing_seconds(adr_rows, sunrise=True)
    sunset_seconds = _solar_crossing_seconds(adr_rows, sunrise=False)
    sunrise = _format_ltst(sunrise_seconds)
    sunset = _format_ltst(sunset_seconds)
    daylight_row_entries = [
        (index, row)
        for index, row in enumerate(rmd_rows, start=1)
        if sunrise_seconds <= _ltst_seconds(row["LTST"]) <= sunset_seconds
    ]
    daylight_rows = [row for _, row in daylight_row_entries]
    uv_values = []
    if rmd_rows and "UV_ABC" in rmd_rows[0]:
        uv_values = [
            value
            for index, row in daylight_row_entries
            if (value := _measurement(row, "UV_ABC", index)) is not None
        ]

    coldest_burst_mean, coldest_burst_samples, burst_count = _coldest_burst(
        rmd_rows, "BRIGHTNESS_TEMP"
    )
    fields: dict[str, object] = {
        "min_temp": round(_celsius(min(ambient_temps))),
        "max_temp": round(_celsius(max(ambient_temps))),
        "mean_temp": _celsius(statistics.mean(ambient_temps)),
        "min_gts_temp": round(_celsius(coldest_burst_mean)),
        "max_gts_temp": round(_celsius(max(gts_temps))),
        "mean_gts_temp": _celsius(statistics.mean(gts_temps)),
        "raw_min_gts_temp": _celsius(min(gts_temps)),
        "pressure": round(statistics.mean(pressures)),
        "min_pressure": round(min(pressures), 2),
        "max_pressure": round(max(pressures), 2),
        "sunrise": sunrise,
        "sunset": sunset,
        "uv_abc_daylight_mean": (
            round(statistics.mean(uv_values), 4) if uv_values else None
        ),
        "uv_abc_daylight_peak": round(max(uv_values), 4) if uv_values else None,
    }

    ground_quality = _metric_quality(
        rmd_rows, len(gts_temps), "GTS_CONFIDENCE_LEVEL"
    )
    ground_quality.update(
        {
            "burst_count": burst_count,
            "coldest_burst_valid_samples": coldest_burst_samples,
            "coldest_burst_mean_celsius": _celsius(coldest_burst_mean),
        }
    )
    quality_summary: dict[str, object] = {
        "missing_value": -999,
        "confidence_policy": (
            "All non-missing measurements are included; confidence flags are "
            "reported but not used to filter."
        ),
        "aggregation": {
            "ground_minimum": (
                "Minimum mean brightness temperature per contiguous acquisition "
                "burst, with a new burst after a gap greater than 60 seconds."
            ),
            "uv_daylight": (
                "RMD samples between the interpolated ADR solar-zenith "
                "crossings at 90 degrees."
            ),
        },
        "products": {
            "rmd_samples": len(rmd_rows),
            "adr_samples": len(adr_rows),
        },
        "metrics": {
            "air_temperature": _metric_quality(
                rmd_rows, len(ambient_temps), "AMBIENT_TEMP_CONFIDENCE_LEVEL"
            ),
            "ground_temperature": ground_quality,
            "pressure": _metric_quality(rmd_rows, len(pressures), "PS_CONFIDENCE_LEVEL"),
            "uv_abc_daylight": {
                **_metric_quality(
                    daylight_rows, len(uv_values), "UVS_CONFIDENCE_LEVEL"
                ),
                "daylight_samples": len(daylight_rows),
                "total_samples": len(rmd_rows),
            },
        },
    }
    return fields, quality_summary
