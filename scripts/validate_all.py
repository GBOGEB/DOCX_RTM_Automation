from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import validate

ROOT = Path(__file__).resolve().parents[1]


def validate_json_file(instance_path: str, schema_path: str) -> None:
    instance = json.loads((ROOT / instance_path).read_text(encoding='utf-8'))
    schema = json.loads((ROOT / schema_path).read_text(encoding='utf-8'))
    validate(instance=instance, schema=schema)


def validate_yaml_file(instance_path: str, schema_path: str) -> None:
    instance = yaml.safe_load((ROOT / instance_path).read_text(encoding='utf-8'))
    schema = json.loads((ROOT / schema_path).read_text(encoding='utf-8'))
    validate(instance=instance, schema=schema)


def main() -> int:
    validate_yaml_file('federation.yaml', 'schemas/federation.schema.json')
    validate_json_file('handover/CURRENT.json', 'schemas/handover.schema.json')
    print('Federation validation passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
