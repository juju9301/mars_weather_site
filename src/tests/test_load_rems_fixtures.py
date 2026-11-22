import json
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from weather.models import Weather


def _write_fixture(directory: Path, sol: int, **overrides):
    fields = {
        "terrestrial_date": "2024-01-01",
        "sol": sol,
        "sunrise": "06:00",
        "sunset": "18:00",
        "source": "NASA PDS REMS RDR",
        "min_gts_temp": -84,
        "raw_min_gts_temp": -139.77,
    }
    fields.update(overrides)
    path = directory / f"weather_sol_{sol}.json"
    path.write_text(
        json.dumps([{"model": "weather.Weather", "fields": fields}]),
        encoding="utf-8",
    )
    return path


class LoadRemsFixturesTests(TestCase):
    def setUp(self):
        temporary_directory = TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        self.fixture_dir = Path(temporary_directory.name)

    def test_updates_existing_sol_when_explicitly_requested(self):
        existing = Weather.objects.create(
            terrestrial_date=date(2024, 1, 1),
            sol=3995,
            sunrise="05:00",
            sunset="17:00",
            source="inta-csic",
            min_gts_temp=-78,
        )
        existing_pk = existing.pk
        _write_fixture(self.fixture_dir, 3995)

        call_command(
            "load_rems_fixtures",
            sol=[3995],
            fixture_dir=self.fixture_dir,
            update_existing=True,
        )

        existing.refresh_from_db()
        self.assertEqual(existing.pk, existing_pk)
        self.assertEqual(existing.source, "NASA PDS REMS RDR")
        self.assertEqual(existing.min_gts_temp, -84)
        self.assertEqual(existing.raw_min_gts_temp, -139.77)

    def test_refuses_to_replace_existing_sol_without_flag(self):
        existing = Weather.objects.create(
            terrestrial_date=date(2024, 1, 1),
            sol=3995,
            sunrise="05:00",
            sunset="17:00",
            source="inta-csic",
            min_gts_temp=-78,
        )
        _write_fixture(self.fixture_dir, 3995)

        with self.assertRaisesMessage(CommandError, "--update-existing"):
            call_command(
                "load_rems_fixtures",
                sol=[3995],
                fixture_dir=self.fixture_dir,
            )

        existing.refresh_from_db()
        self.assertEqual(existing.source, "inta-csic")
        self.assertEqual(existing.min_gts_temp, -78)

    def test_inserts_missing_sol(self):
        _write_fixture(self.fixture_dir, 3996)

        call_command(
            "load_rems_fixtures",
            sol=[3996],
            fixture_dir=self.fixture_dir,
        )

        weather = Weather.objects.get(sol=3996)
        self.assertEqual(weather.source, "NASA PDS REMS RDR")
        self.assertEqual(weather.min_gts_temp, -84)
