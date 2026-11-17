from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from weather.rems_parser import RemsDataError, fixture_json, parse_weather_record


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures"


class Command(BaseCommand):
    help = "Parse a downloaded REMS sol and write a one-record Django fixture."

    def add_arguments(self, parser):
        parser.add_argument("--sol", type=int, required=True)
        parser.add_argument(
            "--data-root",
            type=Path,
            default=REPOSITORY_ROOT / "data" / "sols",
            help="Directory containing one subdirectory per sol (default: data/sols).",
        )
        parser.add_argument(
            "--output",
            type=Path,
            help="Output fixture path (default: weather/fixtures/weather_sol_<sol>.json).",
        )

    def handle(self, *args, **options):
        sol = options["sol"]
        output_path = options["output"] or FIXTURES_DIR / f"weather_sol_{sol}.json"
        try:
            record = parse_weather_record(options["data_root"], sol)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(fixture_json(record), encoding="utf-8")
        except (OSError, RemsDataError) as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(f"Wrote fixture to {output_path}"))
