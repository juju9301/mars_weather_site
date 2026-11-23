# REMS data ingestion

[`parse_rems.py`](./parse_rems.py) turns downloaded calibrated REMS PDS products into Django fixtures. The parser and calculations live in [`src/weather/rems_ingestion`](../src/weather/rems_ingestion/); the existing [`weather.rems_parser`](../src/weather/rems_parser.py) module re-exports its public functions for the Django management command.

## Run it

From the repository root, parse one or more sols:

```powershell
python scripts\parse_rems.py --sol 4843
python scripts\parse_rems.py --sol 4835 4836 4837 --data-root E:\path\to\data_calibrated
```

By default, the script reads `data\sols` and writes `weather_sol_<sol>.json` files to `src\weather\fixtures`. It recognizes numeric sol directories such as `4843`, PDS-style directories such as `SOL04843`, or products placed directly in the data-root. Use `--output-dir` to choose another destination. Existing output files are not replaced unless `--overwrite` is specified.

The fixture has no database primary key and is intended to add a sol that is not already in the database. Since `Weather.sol` is unique, loading a fixture for an existing sol will fail rather than update it. To load a new sol, first migrate and then run from `src`:

```powershell
python manage.py migrate
python manage.py loaddata weather_sol_4843
```

## Input and validation

The parser reads the RMD table for measurements and the ADR table for solar geometry. XML labels provide the table columns and expected row counts; the RMD label provides the terrestrial date from `STOP_TIME`. LTST values are checked against the requested sol. A mismatch, malformed table, invalid numeric value, or missing required product raises an explicit error.

The PDS missing-value sentinel `-999` is excluded from calculations. Temperatures are converted from kelvin to Celsius using `K - 273.15`. Confidence flags are metric-specific: all non-missing values are included, and the original flag-code counts are recorded rather than applying a generic “good” filter.

## Calculated values

| Stored field(s) | Calculation |
| --- | --- |
| `min_temp`, `max_temp` | Minimum and maximum valid `AMBIENT_TEMP` samples, converted to Celsius and rounded to whole degrees. |
| `mean_temp` | Arithmetic mean of valid `AMBIENT_TEMP` samples, converted to Celsius and rounded to two decimal places. |
| `min_gts_temp` | Minimum of the mean `BRIGHTNESS_TEMP` for each acquisition burst, converted to Celsius and rounded to whole degrees. A new burst begins when consecutive LTST readings are more than 60 seconds apart. The legacy database field name is retained for compatibility; a future rename to `coldest_burst_mean` is separate work. |
| `raw_min_gts_temp`, `max_gts_temp` | Raw minimum and maximum valid `BRIGHTNESS_TEMP` samples. The raw minimum is stored in Celsius to two decimal places; the existing maximum is rounded to whole degrees. |
| `mean_gts_temp` | Arithmetic mean of valid `BRIGHTNESS_TEMP` samples, converted to Celsius and rounded to two decimal places. |
| `pressure`, `min_pressure`, `max_pressure` | `pressure` remains the rounded arithmetic mean in Pa. The new minimum and maximum are stored in Pa to two decimal places. |
| `uv_abc_daylight_mean`, `uv_abc_daylight_peak` | Mean and maximum valid `UV_ABC` irradiance samples in W/m², restricted to daylight; values are rounded to four decimal places. |
| `sunrise`, `sunset` | ADR `SOLAR_ZENITHAL_ANGLE` crossings at 90°, linearly interpolated and formatted as LTST `HH:MM`. These crossings also define the daylight window for UV. |

`min_temp`, `max_temp`, and `max_gts_temp` keep their existing integer representation. New mean, pressure-range, raw-minimum, and UV fields are nullable so older records remain valid.

## Quality and interpretation

The `rems_quality_summary` JSON field contains RMD/ADR row counts, valid and total sample counts for each metric, confidence-flag code distributions, and ground-burst details (including burst count and the coldest burst's sample count and unrounded mean). UV coverage includes both the number of daylight samples and the number with a valid UV reading.

The burst rule is a hypothesis, not a confirmed description of INTA's algorithm. It reproduced the legacy minimum after rounding for eight of the nine sols compared in the earlier investigation; Sol 4841 did not match. The gap-based definition can also group long continuous acquisitions: for Sol 4843, the coldest burst contains 7,646 valid readings, produces a coldest-burst mean of about −72.28 °C, and differs substantially from the raw minimum of −118.56 °C. These values and counts are retained separately so the method can be revisited without losing the underlying raw minimum.

Wind, humidity, and rover coordinates are not currently added to the daily summary; their quality or representative-value rules have not been established.
