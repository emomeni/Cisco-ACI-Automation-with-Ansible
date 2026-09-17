"""Check safety boundaries and template syntax in the shipped workflow."""

import json
from pathlib import Path
import sys

from jinja2 import Environment
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "filter_plugins"))
from aci_model import load_model, report_data, snapshot_paths  # noqa: E402


def test_templates_parse():
    environment = Environment()

    def walk(value):
        if isinstance(value, str) and ("{{" in value or "{%" in value):
            environment.parse(value)
        elif isinstance(value, dict):
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    for directory in ["playbooks", "roles", "inventory"]:
        for path in (ROOT / directory).rglob("*.yml"):
            walk(yaml.safe_load(path.read_text(encoding="utf-8")))


def test_report_never_includes_invocation():
    results = [{"changed": True, "item": {"tenant": "TEST"}, "proposed": {"fvTenant": {}},
                "invocation": {"module_args": {"password": "test-fixture"}}, "response": "omit this"}]
    report = report_data(results, "tenants")
    assert report == [{"changed": True, "proposed": {"fvTenant": {}}, "section": "tenants",
                       "identity": {"tenant": "TEST"}}]
    assert "test-fixture" not in json.dumps(report)


def test_snapshot_paths_cover_domains_outside_infra():
    model = load_model((ROOT / "examples/full-stack.yml").read_text())
    paths = snapshot_paths(model)
    assert len(paths) == 4
    assert any("/uni/phys-LAB_PHYS.json?" in path for path in paths)
    assert any("/uni/l3dom-LAB_L3.json?" in path for path in paths)
    assert all("\x01" not in path for path in paths)


def test_tenant_only_capture_needs_no_infra_read():
    model = load_model((ROOT / "examples/tenant-only.yml").read_text())
    assert len(snapshot_paths(model)) == 1


def test_cli_check_mode_cannot_be_overridden_by_apply_flag():
    site = yaml.safe_load((ROOT / "playbooks/site.yml").read_text())[0]
    expression = site["check_mode"]
    environment = Environment()
    environment.filters["bool"] = bool
    for cli_check, apply, expected in [(False, False, "True"), (True, True, "True"),
                                      (True, False, "True"), (False, True, "False")]:
        assert environment.from_string(expression).render(ansible_check_mode=cli_check, aci_apply=apply) == expected


def test_tls_and_collection_defaults():
    site = yaml.safe_load((ROOT / "playbooks/site.yml").read_text())[0]
    defaults = site["module_defaults"]["group/cisco.aci.all"]
    assert defaults["validate_certs"] is True
    assert defaults["use_ssl"] is True
    assert defaults["suppress_previous"] is False
    assert defaults["suppress_verification"] is False


def test_ci_does_not_deploy_or_read_secrets():
    text = (ROOT / ".github/workflows/ci.yml").read_text()
    ci = yaml.safe_load(text)
    assert "pull_request" in ci["on"]
    assert "pull_request_target" not in ci["on"]
    assert ci["permissions"] == {"contents": "read"}
    assert "secrets." not in text
    assert "aci_apply" not in text
    for step in ci["jobs"]["validate"]["steps"]:
        if "uses" in step:
            assert len(step["uses"].split("@")[1]) == 40
