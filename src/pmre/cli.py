from __future__ import annotations

import argparse
import json

from pmre.experiments.maker_markout_smoke import run_smoke
from pmre.reporting.build_feature_diagnostics import build_feature_diagnostics
from pmre.features.build_feature_set_v0_1 import build_feature_set_v0_1
from pmre.features.build_books_features import build_books_features
from pmre.features.freeze_feature_inputs import freeze_feature_inputs
from pmre.reporting.build_tradability_report import build_tradability_report
from pmre.ingest.metadata_refresh import run_metadata_refresh
from pmre.ingest.raw_books_collector import run_raw_books_collection
from pmre.state.build_books_state import build_books_state


def main() -> None:
    parser = argparse.ArgumentParser(description="Polymarket Research Engine CLI")
    subparsers = parser.add_subparsers(dest="command")

    smoke = subparsers.add_parser("smoke", help="Run the minimal smoke pipeline")
    smoke.add_argument("--config", default="configs/base.yaml", help="Path to YAML config")

    metadata = subparsers.add_parser("metadata-refresh", help="Refresh metadata tables from Gamma markets")
    metadata.add_argument("--config", default="configs/base.yaml", help="Path to YAML config")

    raw_books = subparsers.add_parser("raw-books-collect", help="Collect raw CLOB order-book snapshots")
    raw_books.add_argument("--config", default="configs/base.yaml", help="Path to YAML config")

    state_books = subparsers.add_parser("build-books-state", help="Build flat top-of-book state from raw books JSONL")
    state_books.add_argument("--config", default="configs/base.yaml", help="Path to YAML config")
    state_books.add_argument("--input-manifest", default=None, help="Optional path to a raw books manifest JSON")

    freeze_inputs = subparsers.add_parser("freeze-feature-inputs", help="Freeze the approved input set for the feature job")
    freeze_inputs.add_argument("--config", default="configs/base.yaml", help="Path to YAML config")

    feature_v0_1 = subparsers.add_parser("build-feature-set-v0-1", help="Build the minimum stable feature set v0_1")
    feature_v0_1.add_argument("--config", default="configs/base.yaml", help="Path to YAML config")

    books_features = subparsers.add_parser("build-books-features", help="Build books-derived features from the latest books-state manifest")
    books_features.add_argument("--config", default="configs/base.yaml", help="Path to YAML config")

    feature_diagnostics = subparsers.add_parser(
        "build-feature-diagnostics",
        help="Build diagnostics from the latest stable feature-set manifest",
    )
    feature_diagnostics.add_argument("--config", default="configs/base.yaml", help="Path to YAML config")

    tradability_report = subparsers.add_parser(
        "build-tradability-report",
        help="Build market gating + active universe report from diagnostics outputs",
    )
    tradability_report.add_argument("--config", default="configs/base.yaml", help="Path to YAML config")

    args = parser.parse_args()

    if args.command == "smoke":
        result = run_smoke(args.config)
        print(json.dumps(result, indent=2))
        return

    if args.command == "metadata-refresh":
        result = run_metadata_refresh(args.config)
        print(json.dumps(result, indent=2))
        return

    if args.command == "raw-books-collect":
        result = run_raw_books_collection(args.config)
        print(json.dumps(result, indent=2))
        return

    if args.command == "build-books-state":
        result = build_books_state(args.config, input_manifest_path=args.input_manifest)
        print(json.dumps(result, indent=2))
        return

    if args.command == "freeze-feature-inputs":
        result = freeze_feature_inputs(args.config)
        print(json.dumps(result, indent=2))
        return

    if args.command == "build-feature-set-v0-1":
        result = build_feature_set_v0_1(args.config)
        print(json.dumps(result, indent=2))
        return

    if args.command == "build-books-features":
        result = build_books_features(args.config)
        print(json.dumps(result, indent=2))
        return

    if args.command == "build-feature-diagnostics":
        result = build_feature_diagnostics(args.config)
        print(json.dumps(result, indent=2))
        return

    if args.command == "build-tradability-report":
        result = build_tradability_report(args.config)
        print(json.dumps(result, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
