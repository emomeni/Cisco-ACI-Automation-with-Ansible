#!/usr/bin/env python3
"""Validate intent offline; exits nonzero before any controller connection."""

import argparse
from pathlib import Path
import sys

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "filter_plugins"))
from aci_model import load_model  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("models", nargs="+", type=Path)
    args = parser.parse_args()
    for path in args.models:
        try:
            model = load_model(path.read_text(encoding="utf-8"))
        except (ValueError, OSError, yaml.YAMLError) as error:
            parser.exit(1, f"INVALID {path}: {error}\n")
        count = sum(len(value) for value in model.values() if isinstance(value, list))
        print(f"VALID {path}: {count} managed objects")


if __name__ == "__main__":
    main()
