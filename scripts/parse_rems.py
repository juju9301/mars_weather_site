import argparse
import logging
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from weather.rems_ingestion import (  # noqa: E402
    RemsDataError,
    fixture_json,
    parse_weather_records,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Parse downloaded REMS products into Django weather fixtures."
    )
    parser.add_argument("--sol", type=int, nargs="+", required=True)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=REPOSITORY_ROOT / "data" / "sols",
        help="Directory containing per-sol product folders (default: data/sols).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=SOURCE_ROOT / "weather" / "fixtures",
        help="Directory for generated fixtures.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace generated fixture files that already exist.",
    )
    args = parser.parse_args(argv)

    if any(sol < 0 for sol in args.sol):
        parser.error("Sol numbers must be non-negative.")
    if len(set(args.sol)) != len(args.sol):
        parser.error("Sol numbers must be unique.")
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stdout,
    )

    output_paths = [
        args.output_dir / f"weather_sol_{sol}.json" for sol in args.sol
    ]
    if not args.overwrite:
        existing_paths = [path for path in output_paths if path.exists()]
        if existing_paths:
            parser.error(
                "Output already exists; pass --overwrite to replace it: "
                + ", ".join(str(path) for path in existing_paths)
            )

    try:
        records = parse_weather_records(
            args.data_root,
            args.sol,
            logger=logging.getLogger("rems_ingestion"),
        )
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for path, record in zip(output_paths, records):
            path.write_text(fixture_json(record), encoding="utf-8")
    except (OSError, RemsDataError) as exc:
        print(f"Could not generate REMS fixture: {exc}", file=sys.stderr)
        return 1

    for path in output_paths:
        print(f"Wrote fixture to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
