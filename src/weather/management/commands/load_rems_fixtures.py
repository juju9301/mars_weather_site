import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from weather.models import Weather


FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures"


class Command(BaseCommand):
    help = "Insert or explicitly update weather rows from generated REMS fixtures."

    def add_arguments(self, parser):
        parser.add_argument("--sol", type=int, nargs="+", required=True)
        parser.add_argument(
            "--fixture-dir",
            type=Path,
            default=FIXTURES_DIR,
            help="Directory containing weather_sol_<sol>.json files.",
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Replace fields on existing sols while preserving their database IDs.",
        )

    def handle(self, *args, **options):
        sols = options["sol"]
        if any(sol < 0 for sol in sols):
            raise CommandError("Sol numbers must be non-negative.")
        if len(set(sols)) != len(sols):
            raise CommandError("Sol numbers must be unique.")

        fixtures = [
            (sol, self._read_fixture(options["fixture_dir"], sol))
            for sol in sols
        ]
        existing_sols = set(
            Weather.objects.filter(sol__in=sols).values_list("sol", flat=True)
        )
        conflicts = sorted(existing_sols)
        if conflicts and not options["update_existing"]:
            formatted = ", ".join(str(sol) for sol in conflicts)
            raise CommandError(
                f"Sol(s) {formatted} already exist. Re-run with "
                "--update-existing to replace their REMS-derived fields."
            )

        with transaction.atomic():
            for sol, fields in fixtures:
                defaults = {
                    key: value for key, value in fields.items() if key != "sol"
                }
                weather, created = Weather.objects.update_or_create(
                    sol=sol,
                    defaults=defaults,
                )
                action = "Created" if created else "Updated"
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{action} Sol {sol} (database id {weather.pk})."
                    )
                )

    @staticmethod
    def _read_fixture(fixture_dir: Path, sol: int) -> dict[str, Any]:
        fixture_path = fixture_dir / f"weather_sol_{sol}.json"
        try:
            fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CommandError(
                f"Could not read fixture {fixture_path}: {exc}"
            ) from exc

        if (
            not isinstance(fixture, list)
            or len(fixture) != 1
            or not isinstance(fixture[0], dict)
        ):
            raise CommandError(
                f"Expected exactly one fixture record in {fixture_path}."
            )
        record = fixture[0]
        if record.get("model") != "weather.Weather":
            raise CommandError(
                f"Fixture {fixture_path} must contain a weather.Weather record."
            )
        fields = record.get("fields")
        if not isinstance(fields, dict) or fields.get("sol") != sol:
            raise CommandError(
                f"Fixture {fixture_path} must contain fields for sol {sol}."
            )

        model_fields = {
            field.name
            for field in Weather._meta.concrete_fields
            if not field.primary_key
        }
        unknown_fields = set(fields) - model_fields
        if unknown_fields:
            raise CommandError(
                f"Fixture {fixture_path} contains unknown Weather fields: "
                f"{', '.join(sorted(unknown_fields))}."
            )
        return fields
