"""Behavior tests for configuration boundaries; these never connect to APIC."""

import copy
from pathlib import Path
import sys

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "filter_plugins"))
from aci_model import load_model, snapshot_data, validate_model  # noqa: E402


@pytest.fixture
def model():
    return load_model((ROOT / "examples/full-stack.yml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("filename", ["full-stack.yml", "tenant-only.yml"])
def test_valid_examples(filename):
    load_model((ROOT / "examples" / filename).read_text(encoding="utf-8"))


@pytest.mark.parametrize("section,field,value", [
    ("tenants", "tenant", "common"),
    ("tenants", "tenant", "infra"),
    ("tenants", "tenant", "mgmt"),
    ("tenants", "tenant", "path/escape"),
    ("tenants", "description", "{{ lookup('env', 'SECRET') }}"),
    ("vrfs", "policy_control_preference", "unenforced"),
    ("bridge_domains", "vrf", "MISSING"),
    ("bridge_domains", "enable_routing", False),
    ("epgs", "preferred_group", True),
    ("epgs", "bd", "MISSING"),
    ("filter_entries", "destination_port_end", "80"),
    ("filter_entries", "destination_port_start", "65536"),
    ("vlan_blocks", "block_end", 4095),
    ("vlan_blocks", "block_end", 100),
    ("subnets", "gateway", "10.20.110.0"),
    ("subnets", "gateway", "2001:db8::1"),
    ("subnets", "scope", ["public", "private"]),
    ("static_bindings", "encap_id", 200),
    ("static_bindings", "interface", "1/11"),
    ("static_bindings", "interface_type", "vpc"),
    ("static_bindings", "leafs", ["101", "102"]),
    ("static_nexthops", "nexthop", "203.0.113.1"),
    ("static_nexthops", "nexthop", "192.0.2.2"),
    ("static_nexthops", "nexthop", "192.0.2.0"),
    ("l3out_interfaces", "path_ep", "eth1/10"),
    ("l3out_interfaces", "address", "192.0.2.0/30"),
    ("l3out_interfaces", "mtu", "9999"),
    ("l3outs", "l3protocol", ["bgp"]),
    ("leaf_selectors", "to", 100),
    ("epg_domains", "domain", "MISSING"),
    ("access_ports", "to_port", "9"),
    ("subject_filters", "filter", "MISSING"),
])
def test_reject_invalid_values(model, section, field, value):
    model[section][0][field] = value
    with pytest.raises(ValueError):
        validate_model(model)


@pytest.mark.parametrize("section", ["tenants", "vrfs", "subnets", "static_bindings", "domain_pools"])
def test_duplicate_identities(model, section):
    model[section].append(copy.deepcopy(model[section][0]))
    with pytest.raises(ValueError, match="Duplicate object"):
        validate_model(model)


@pytest.mark.parametrize("section", ["tenants", "static_nexthops", "aep_domains", "domain_pools", "bd_l3outs"])
def test_missing_required_dependencies(model, section):
    model[section] = []
    with pytest.raises(ValueError):
        validate_model(model)


@pytest.mark.parametrize("field,value", [("state", "absent"), ("host", "other.example.com"),
                                        ("validate_certs", False), ("password", "test-fixture")])
def test_no_module_or_security_overrides(model, field, value):
    model["tenants"][0][field] = value
    with pytest.raises(ValueError):
        validate_model(model)


def test_unknown_section(model):
    model["tenantz"] = []
    with pytest.raises(ValueError):
        validate_model(model)


def test_overlap_subnets(model):
    model["subnets"].append(dict(model["subnets"][0], gateway="10.20.110.129", mask=25))
    with pytest.raises(ValueError, match="Overlapping BD"):
        validate_model(model)


def test_overlap_vlan_blocks(model):
    model["vlan_blocks"].append(dict(model["vlan_blocks"][0], block_start=115, block_end=125))
    with pytest.raises(ValueError, match="Overlapping VLAN"):
        validate_model(model)


def test_overlap_access_selectors(model):
    model["access_ports"].append(dict(model["access_ports"][0], access_port_selector="OTHER"))
    with pytest.raises(ValueError, match="Overlapping access"):
        validate_model(model)


def test_route_network_must_be_canonical(model):
    model["static_routes"][0]["prefix"] = "10.0.0.1/24"
    model["static_nexthops"][0]["prefix"] = "10.0.0.1/24"
    with pytest.raises(ValueError):
        validate_model(model)


def test_same_subnet_in_different_vrf_allowed(model):
    model["vrfs"].append(dict(model["vrfs"][0], vrf="OTHER"))
    model["bridge_domains"].append(dict(model["bridge_domains"][0], bd="OTHER", vrf="OTHER"))
    model["subnets"].append(dict(model["subnets"][0], bd="OTHER", scope=["private"]))
    validate_model(model)


def test_duplicate_yaml_keys_rejected():
    with pytest.raises(ValueError, match="Duplicate YAML key"):
        load_model("schema_version: 1\nschema_version: 1\n")


def test_anchors_rejected():
    with pytest.raises(ValueError, match="anchors"):
        load_model("a: &value 1\nb: *value\n")


def test_unsafe_yaml_tag_rejected():
    with pytest.raises(yaml.YAMLError):
        load_model("!!python/object/apply:os.system ['echo unsafe']")


def test_snapshot_excludes_invocation():
    data = snapshot_data([{"item": "/api/mo/uni.json", "imdata": [],
                           "invocation": {"module_args": {"password": "test-fixture"}}}])
    assert data == [{"path": "/api/mo/uni.json", "imdata": []}]
