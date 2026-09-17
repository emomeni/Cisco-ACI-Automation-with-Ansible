#!/usr/bin/env python3
"""Check task parameters against the installed, pinned collection source."""

import argparse
import ast
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", type=Path,
                        default=ROOT / ".ansible/collections/ansible_collections/cisco/aci")
    args = parser.parse_args()
    registry = json.loads((ROOT / "schemas/resources.json").read_text())
    schema = json.loads((ROOT / "schemas/aci.schema.json").read_text())
    manifest = args.collection / "MANIFEST.json"
    if manifest.exists():
        assert json.loads(manifest.read_text())["collection_info"]["version"] == "2.13.0"
    else:
        assert yaml.safe_load((args.collection / "galaxy.yml").read_text())["version"] == "2.13.0"
    tasks = [task for path in (ROOT / "roles").glob("*/tasks/main.yml")
             for task in yaml.safe_load(path.read_text())]
    for section, resource in registry.items():
        module = resource["module"]
        source = (args.collection / "plugins/modules" / (module.split(".")[-1] + ".py")).read_text(encoding="utf-8")
        tree = ast.parse(source)
        doc = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "DOCUMENTATION" for t in n.targets))
        options = yaml.safe_load(doc)["options"]
        assert set(resource["parameters"]) <= set(options), module
        # The runtime argument_spec must contain all parameters, not only its documentation.
        runtime_keys = {keyword.arg for node in ast.walk(tree) if isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute) and node.func.attr == "update"
                        and isinstance(node.func.value, ast.Name) and node.func.value.id == "argument_spec"
                        for keyword in node.keywords}
        runtime_keys.update(key.value for node in ast.walk(tree) if isinstance(node, ast.Call)
                            and isinstance(node.func, ast.Attribute) and node.func.attr == "update"
                            and isinstance(node.func.value, ast.Name) and node.func.value.id == "argument_spec"
                            for arg in node.args if isinstance(arg, ast.Dict)
                            for key in arg.keys if isinstance(key, ast.Constant))
        assert set(resource["parameters"]) <= runtime_keys, f"Runtime arguments: {module}"
        assert any(isinstance(node, ast.keyword) and node.arg == "supports_check_mode"
                   and isinstance(node.value, ast.Constant) and node.value.value is True
                   for node in ast.walk(tree)), f"No check mode: {module}"
        task = next(task for task in tasks if module in task)
        assert set(task[module]) == set(resource["parameters"]) | {"state"}
        assert task[module]["state"] == "present" and task["no_log"] is True
        for field, definition in schema["properties"][section]["items"]["properties"].items():
            choices = options[field].get("choices")
            if not choices:
                continue
            selected = definition.get("enum", definition.get("items", {}).get("enum", []))
            if "const" in definition:
                selected = definition["const"] if isinstance(definition["const"], list) else [definition["const"]]
            assert set(selected) <= set(choices), f"Unsupported choices: {module}.{field}"
    print(f"PASS: {len(registry)} modules match cisco.aci 2.13.0 source contracts")


if __name__ == "__main__":
    main()
