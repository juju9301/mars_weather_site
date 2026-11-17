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
    "HORIZONTAL_WIND_SPEED",
    "WIND_DIRECTION",
    "BRIGHTNESS_TEMP",
    "AMBIENT_TEMP",
    "PRESSURE",
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
                    "2", "350", "180", "200", "800",
                ],
                [
                    "2", "04843M12:00:00", "04843 12:00:00",
                    "4", "10", "200", "220", "1000",
                ],
                [
                    "3", "04843M13:00:00", "04843 13:00:00",
                    "-999", "-999", "-999", "-999", "-999",
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
        self.assertEqual(fields["pressure"], 900)
        self.assertEqual(fields["wind_speed"], "3.00")
        self.assertEqual(fields["wind_direction"], "0.00")
        self.assertEqual((fields["sunrise"], fields["sunset"]), ("05:30", "17:30"))
        self.assertEqual((fields["min_gts_temp"], fields["max_gts_temp"]), (-93, -73))
        self.assertIsNone(fields["atmo_opacity"])

    def test_generated_fixture_loads_without_a_source_primary_key(self):
        self._write_sample_tables(
            [["1", "04843M05:00:00", "04843 05:00:00", "2", "180", "180", "200", "800"]],
        )
        record = parse_weather_record(self.data_root, SOL)
        fixture_path = self.directory / "weather_sol_4843.json"
        fixture_path.write_text(fixture_json(record), encoding="utf-8")

        call_command("loaddata", str(fixture_path), verbosity=0)

        from weather.models import Weather

        weather = Weather.objects.get(sol=SOL)
        self.assertIsNone(weather.orig_id)
        self.assertEqual(weather.source, "NASA PDS REMS RDR")

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
