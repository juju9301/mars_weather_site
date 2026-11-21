import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import TestCase

from weather.rems_parser import fixture_json, parse_weather_record


SOL = 4843
RMD_COLUMNS = [
    "TIMESTAMP",
    "LMST",
    "LTST",
    "BRIGHTNESS_TEMP",
    "GTS_CONFIDENCE_LEVEL",
    "AMBIENT_TEMP",
    "AMBIENT_TEMP_CONFIDENCE_LEVEL",
    "UV_ABC",
    "UVS_CONFIDENCE_LEVEL",
    "PRESSURE",
    "PS_CONFIDENCE_LEVEL",
]
ADR_COLUMNS = [
    "TIMESTAMP",
    "LMST",
    "LTST",
    "SOLAR_LONGITUDE_ANGLE",
    "SOLAR_ZENITHAL_ANGLE",
]


def _write_product(directory: Path, product: str, columns: list[str], rows):
    stem = f"RME_TEST{product}{SOL}"
    xml_fields = "".join(
        f"<Field_Character><name>{name}</name></Field_Character>"
        for name in columns
    )
    (directory / f"{stem}.xml").write_text(
        "<Product_Observational><File_Area_Observational>"
        f"<Table_Character><records>{len(rows)}</records>{xml_fields}"
        "</Table_Character></File_Area_Observational></Product_Observational>",
        encoding="utf-8",
    )
    with (directory / f"{stem}.TAB").open("w", encoding="ascii", newline="") as out:
        csv.writer(out).writerows(rows)


class RemsParserTests(TestCase):
    def setUp(self):
        temporary_directory = TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.data_root = Path(temporary_directory.name)
        self.directory = self.data_root / str(SOL)
        self.directory.mkdir()
        (self.directory / f"RME_TESTRMD{SOL}.LBL").write_text(
            "PLANET_DAY_NUMBER = 4843\n"
            "STOP_TIME = 2026-03-22T12:03:18.021\n",
            encoding="utf-8",
        )

    def _write_sample_tables(self, rmd_rows):
        _write_product(self.directory, "RMD", RMD_COLUMNS, rmd_rows)
        _write_product(
            self.directory,
            "ADR",
            ADR_COLUMNS,
            [
                ["1", "04843M05:00:00", "04843 05:00:00", "247", "100"],
                ["2", "04843M06:00:00", "04843 06:00:00", "247", "80"],
                ["3", "04843M17:00:00", "04843 17:00:00", "247", "80"],
                ["4", "04843M18:00:00", "04843 18:00:00", "247", "100"],
            ],
        )

    def test_builds_fixture_values_from_labeled_tables(self):
        self._write_sample_tables(
            [
                [
                    "1", "04843M05:00:00", "04843 05:00:00",
                    "180", "0111", "200", "111111111", "-999", "11001",
                    "800", "11",
                ],
                [
                    "2", "04843M05:00:30", "04843 05:00:30",
                    "182", "0111", "202", "111111111", "-999", "11001",
                    "810", "11",
                ],
                [
                    "2", "04843M12:00:00", "04843 12:00:00",
                    "200", "0111", "220", "111111111", "1.2", "11001",
                    "1000", "11",
                ],
                [
                    "3", "04843M13:00:00", "04843 13:00:00",
                    "-999", "XXXX", "-999", "XXXXXXXXX", "-999", "XXXXX",
                    "-999", "XX",
                ],
            ],
        )

        record = parse_weather_record(self.data_root, SOL)
        fields = record["fields"]
        self.assertEqual(record["model"], "weather.Weather")
        self.assertIsNone(fields["orig_id"])
        self.assertEqual(fields["terrestrial_date"], "2026-03-22")
        self.assertIsNone(fields["ls"])
        self.assertIsNone(fields["season"])
        self.assertEqual((fields["min_temp"], fields["max_temp"]), (-73, -53))
        self.assertAlmostEqual(fields["mean_temp"], -65.82)
        self.assertEqual(fields["pressure"], 870)
        self.assertEqual((fields["min_pressure"], fields["max_pressure"]), (800, 1000))
        self.assertEqual((fields["sunrise"], fields["sunset"]), ("05:30", "17:30"))
        self.assertEqual((fields["min_gts_temp"], fields["max_gts_temp"]), (-92, -73))
        self.assertAlmostEqual(fields["mean_gts_temp"], -85.82)
        self.assertEqual(fields["raw_min_gts_temp"], -93.15)
        self.assertEqual(fields["uv_abc_daylight_mean"], 1.2)
        self.assertEqual(fields["uv_abc_daylight_peak"], 1.2)
        quality = fields["rems_quality_summary"]
        self.assertEqual(
            quality["metrics"]["ground_temperature"]["valid_samples"], 3
        )
        self.assertEqual(
            quality["metrics"]["ground_temperature"]["confidence_flag_counts"],
            {"0111": 3, "XXXX": 1},
        )
        self.assertEqual(
            quality["metrics"]["ground_temperature"]["burst_count"], 2
        )
        self.assertEqual(
            quality["metrics"]["ground_temperature"]["coldest_burst_valid_samples"],
            2,
        )
        self.assertEqual(
            quality["metrics"]["ground_temperature"]["coldest_burst_mean_celsius"],
            -92.15,
        )
        self.assertEqual(
            quality["metrics"]["uv_abc_daylight"]["daylight_samples"], 2
        )
        self.assertIn("not used to filter", quality["confidence_policy"])
        self.assertNotIn("abs_humidity", fields)
        self.assertNotIn("wind_speed", fields)
        self.assertNotIn("wind_direction", fields)
        self.assertNotIn("atmo_opacity", fields)

    def test_generated_fixture_loads_without_a_source_primary_key(self):
        self._write_sample_tables(
            [[
                "1", "04843M05:00:00", "04843 05:00:00",
                "180", "0111", "200", "111111111", "-999", "11001",
                "800", "11",
            ]],
        )
        record = parse_weather_record(self.data_root, SOL)
        fixture_path = self.directory / "weather_sol_4843.json"
        fixture_path.write_text(fixture_json(record), encoding="utf-8")

        call_command("loaddata", str(fixture_path), verbosity=0)

        from weather.models import Weather

        weather = Weather.objects.get(sol=SOL)
        self.assertIsNone(weather.orig_id)
        self.assertEqual(weather.source, "NASA PDS REMS RDR")
        self.assertEqual(weather.raw_min_gts_temp, -93.15)

    def test_reads_padded_sol_directory_names(self):
        self._write_sample_tables(
            [[
                "1", "04843M05:00:00", "04843 05:00:00",
                "180", "0111", "200", "111111111", "-999", "11001",
                "800", "11",
            ]],
        )
        self.directory.rename(self.data_root / "SOL04843")

        record = parse_weather_record(self.data_root, SOL)

        self.assertEqual(record["fields"]["sol"], SOL)

    def test_reads_text_label_fallback_when_no_label_is_present(self):
        self._write_sample_tables(
            [[
                "1", "04843M05:00:00", "04843 05:00:00",
                "180", "0111", "200", "111111111", "-999", "11001",
                "800", "11",
            ]],
        )
        label_path = self.directory / f"RME_TESTRMD{SOL}.LBL"
        label_path.rename(label_path.with_suffix(".LBL.txt"))

        record = parse_weather_record(self.data_root, SOL)

        self.assertEqual(record["fields"]["sol"], SOL)

    def test_all_ci_weather_fixtures_load_together(self):
        fixture_dir = Path(__file__).resolve().parents[1] / "weather" / "fixtures"
        fixture_paths = [
            fixture_dir / "weather_fixture.json",
            *sorted(fixture_dir.glob("weather_sol_*.json")),
        ]
        call_command("loaddata", *(str(path) for path in fixture_paths), verbosity=0)

        from weather.models import Weather

        expected_count = sum(
            len(json.loads(path.read_text(encoding="utf-8")))
            for path in fixture_paths
        )
        self.assertEqual(Weather.objects.count(), expected_count)
        self.assertTrue(Weather.objects.filter(sol=SOL).exists())
