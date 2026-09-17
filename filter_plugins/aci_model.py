"""Strict intent validation; no network access and no configuration mutations."""

import ipaddress
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/aci.schema.json").read_text(encoding="utf-8"))
RESOURCES = json.loads((ROOT / "schemas/resources.json").read_text(encoding="utf-8"))


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate mapping keys, including collisions introduced by merges."""


def unique_mapping(loader, node, deep=False):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ValueError("YAML mapping keys must be strings")
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)


def load_model(raw):
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > 2_000_000:
        raise ValueError("Intent must be YAML text smaller than 2 MB")
    # Intent is data, never a template or an alias graph.
    for token in yaml.scan(raw):
        if isinstance(token, (yaml.tokens.AliasToken, yaml.tokens.AnchorToken)):
            raise ValueError("YAML anchors and aliases are not accepted in intent")
    model = yaml.load(raw, Loader=UniqueKeyLoader)
    return validate_model(model)


def validate_model(model):
    errors = sorted(
        Draft202012Validator(SCHEMA).iter_errors(model),
        key=lambda error: str(list(error.absolute_path)),
    )
    if errors:
        # Report location and rule, without echoing potentially sensitive input.
        error = errors[0]
        location = ".".join(map(str, error.absolute_path)) or "root"
        raise ValueError(f"Invalid intent at {location}: {error.validator}")

    def plain(value):
        if isinstance(value, str) and any(s in value for s in ("{{", "{%", "{#")):
            raise ValueError("Templates are not permitted in intent")
        if isinstance(value, dict):
            for child in value.values():
                plain(child)
        elif isinstance(value, list):
            for child in value:
                plain(child)

    plain(model)
    if not model["tenants"]:
        raise ValueError("At least one explicitly managed tenant is required")
    if any(t["tenant"].lower() in {"common", "infra", "mgmt"} for t in model["tenants"]):
        raise ValueError("Built-in tenants are outside this repository's managed scope")

    indexes = {}
    for section, spec in RESOURCES.items():
        indexes[section] = {}
        for item in model.get(section, []):
            key = tuple(json.dumps(item[field], sort_keys=True) for field in spec["identity"])
            if key in indexes[section]:
                raise ValueError(f"Duplicate object identity in {section}")
            indexes[section][key] = item

    def find(section, **fields):
        matches = [
            item for item in model.get(section, [])
            if all(str(item.get(key)) == str(value) for key, value in fields.items())
        ]
        if len(matches) != 1:
            raise ValueError(f"Expected one managed reference in {section} ({', '.join(fields)})")
        return matches[0]

    # Every parent and relationship must resolve inside the declared model.
    references = {
        "vlan_blocks": [("vlan_pools", "pool pool_allocation_mode")],
        "domain_pools": [("domains", "domain domain_type"), ("vlan_pools", "pool pool_allocation_mode")],
        "aep_domains": [("aeps", "aep"), ("domains", "domain domain_type")],
        "access_policy_groups": [("aeps", "aep"), ("link_policies", "link_level_policy"),
                                 ("lldp_policies", "lldp_policy"), ("cdp_policies", "cdp_policy")],
        "access_ports": [("interface_profiles", "interface_profile"), ("access_policy_groups", "policy_group")],
        "leaf_selectors": [("leaf_profiles", "leaf_profile")],
        "leaf_interfaces": [("leaf_profiles", "leaf_profile"), ("interface_profiles", "interface_profile:interface_selector")],
        "bridge_domains": [("vrfs", "tenant vrf")],
        "subnets": [("bridge_domains", "tenant bd")],
        "epgs": [("applications", "tenant ap"), ("bridge_domains", "tenant bd")],
        "filter_entries": [("filters", "tenant filter")],
        "subjects": [("contracts", "tenant contract")],
        "subject_filters": [("subjects", "tenant contract subject"), ("filters", "tenant filter")],
        "epg_contracts": [("epgs", "tenant ap epg"), ("contracts", "tenant contract")],
        "l3outs": [("vrfs", "tenant vrf")],
        "l3out_node_profiles": [("l3outs", "tenant l3out")],
        "l3out_nodes": [("l3out_node_profiles", "tenant l3out node_profile")],
        "l3out_interface_profiles": [("l3out_node_profiles", "tenant l3out node_profile")],
        "l3out_interfaces": [("l3out_interface_profiles", "tenant l3out node_profile interface_profile"),
                             ("l3out_nodes", "tenant l3out node_profile pod_id node_id")],
        "static_routes": [("l3out_nodes", "tenant l3out node_profile:logical_node pod_id node_id")],
        "static_nexthops": [("static_routes", "tenant l3out logical_node:node_profile pod_id node_id prefix")],
        "external_epgs": [("l3outs", "tenant l3out")],
        "external_subnets": [("external_epgs", "tenant l3out extepg")],
        "external_contracts": [("external_epgs", "tenant l3out extepg"), ("contracts", "tenant contract")],
        "bd_l3outs": [("bridge_domains", "tenant bd"), ("l3outs", "tenant l3out")],
        "epg_domains": [("epgs", "tenant ap epg"), ("domains", "domain domain_type")],
        "static_bindings": [("epgs", "tenant ap epg")],
    }
    for section in RESOURCES:
        for item in model.get(section, []):
            if "tenant" in item and section != "tenants":
                find("tenants", tenant=item["tenant"])
            for target, mapping in references.get(section, []):
                fields = {}
                for pair in mapping.split():
                    dest, source = pair.split(":") if ":" in pair else (pair, pair)
                    fields[dest] = item[source]
                find(target, **fields)

    def ipv4(value, network=False, interface=False):
        parser = ipaddress.ip_interface if interface else ipaddress.ip_network if network else ipaddress.ip_address
        parsed = parser(value)
        if parsed.version != 4:
            raise ValueError("This model supports IPv4; IPv6 requires a separately tested extension")
        return parsed

    pools = {}
    for block in model.get("vlan_blocks", []):
        start, end = block["block_start"], block["block_end"]
        if start > end:
            raise ValueError("Reversed VLAN range")
        key = (block["pool"], block["pool_allocation_mode"])
        ranges = pools.setdefault(key, [])
        if any(start <= previous_end and end >= previous_start for previous_start, previous_end in ranges):
            raise ValueError("Overlapping VLAN blocks in one pool")
        ranges.append((start, end))

    nets = []
    for subnet in model.get("subnets", []):
        address = ipv4(f'{subnet["gateway"]}/{subnet["mask"]}', interface=True)
        if address.network.prefixlen < 31 and address.ip in (address.network.network_address, address.network.broadcast_address):
            raise ValueError("BD gateway cannot be a network or broadcast address")
        bd = find("bridge_domains", tenant=subnet["tenant"], bd=subnet["bd"])
        if not bd["enable_routing"]:
            raise ValueError("A BD subnet requires routing enabled in this model")
        scope = (subnet["tenant"], bd["vrf"])
        if any(scope == prior_scope and address.network.overlaps(prior) for prior_scope, prior in nets):
            raise ValueError("Overlapping BD subnets within one VRF")
        nets.append((scope, address.network))
        if len(subnet["scope"]) != 1:
            raise ValueError("Choose exactly one BD subnet scope: private or public")
        if "public" in subnet["scope"] and not any(
            row["tenant"] == subnet["tenant"] and row["bd"] == subnet["bd"]
            for row in model.get("bd_l3outs", [])
        ):
            raise ValueError("Public BD subnet requires a managed BD-to-L3Out relationship")

    for entry in model.get("filter_entries", []):
        if not 1 <= int(entry["destination_port_start"]) <= int(entry["destination_port_end"]) <= 65535:
            raise ValueError("Invalid transport port range")
        if entry.get("stateful", False) and entry["ip_protocol"] != "tcp":
            raise ValueError("Stateful matching is supported only for TCP")

    for relation in model.get("bd_l3outs", []):
        bd = find("bridge_domains", tenant=relation["tenant"], bd=relation["bd"])
        l3out = find("l3outs", tenant=relation["tenant"], l3out=relation["l3out"])
        if bd["vrf"] != l3out["vrf"]:
            raise ValueError("BD and L3Out must use the same VRF")

    # Build the actual leaf/port -> AEP path and reject selector collisions.
    port_paths = {}
    for selector in model.get("leaf_selectors", []):
        if selector["from"] > selector["to"]:
            raise ValueError("Reversed leaf range")
    for binding in model.get("leaf_interfaces", []):
        selectors = [s for s in model.get("leaf_selectors", []) if s["leaf_profile"] == binding["leaf_profile"]]
        for port in model.get("access_ports", []):
            if port["interface_profile"] != binding["interface_selector"]:
                continue
            start, end = int(port["from_port"]), int(port["to_port"])
            if not 1 <= start <= end <= 512:
                raise ValueError("Invalid access port range")
            group = find("access_policy_groups", policy_group=port["policy_group"])
            for selector in selectors:
                for leaf in range(selector["from"], selector["to"] + 1):
                    for number in range(start, end + 1):
                        key = (leaf, f"1/{number}")
                        if key in port_paths:
                            raise ValueError("Overlapping access selectors on the same leaf/port")
                        port_paths[key] = group["aep"]

    occupied = set()
    for binding in model.get("static_bindings", []):
        key = (int(binding["leafs"][0]), binding["interface"])
        if key not in port_paths:
            raise ValueError("Static EPG path has no complete managed access-policy chain")
        aep = port_paths[key]
        matched = False
        for domain in model.get("epg_domains", []):
            if not all(domain[f] == binding[f] for f in ("tenant", "ap", "epg")):
                continue
            if not any(d["aep"] == aep and d["domain"] == domain["domain"] and d["domain_type"] == "phys"
                       for d in model.get("aep_domains", [])):
                continue
            pool = find("domain_pools", domain=domain["domain"], domain_type="phys")
            if any(start <= binding["encap_id"] <= end for start, end in pools.get((pool["pool"], "static"), [])):
                matched = True
        if not matched:
            raise ValueError("Static binding VLAN is not reachable through its EPG domain, AEP and pool")
        occupied.add(key)
    # One encapsulation can map to only one EPG on a physical path.
    binding_keys = set()
    untagged_keys = set()
    for binding in model.get("static_bindings", []):
        path = (binding["pod_id"], binding["leafs"][0], binding["interface"])
        encap_key = path + (binding["encap_id"],)
        if encap_key in binding_keys:
            raise ValueError("Duplicate VLAN on one static path")
        binding_keys.add(encap_key)
        if binding["interface_mode"] in {"access", "native", "untagged", "802.1p"}:
            if path in untagged_keys:
                raise ValueError("Multiple untagged/native EPG bindings on one path")
            untagged_keys.add(path)

    routed = set()
    for interface in model.get("l3out_interfaces", []):
        key = (int(interface["node_id"]), interface["path_ep"].removeprefix("eth"))
        if key in occupied or key in routed:
            raise ValueError("L3Out routed port conflicts with another binding")
        routed.add(key)
        if key not in port_paths:
            raise ValueError("L3Out interface has no complete managed access-policy chain")
        if not 576 <= int(interface["mtu"]) <= 9216:
            raise ValueError("Unsupported MTU")
        address = ipv4(interface["address"], interface=True)
        if address.network.prefixlen < 31 and address.ip in (address.network.network_address, address.network.broadcast_address):
            raise ValueError("L3Out address cannot be a network or broadcast address")
        if int(interface["pod_id"]) > 255 or int(interface["node_id"]) > 4000:
            raise ValueError("Invalid L3Out pod/node identifier")
        out = find("l3outs", tenant=interface["tenant"], l3out=interface["l3out"])
        find("aep_domains", aep=port_paths[key], domain=out["domain"], domain_type="l3dom")
    for out in model.get("l3outs", []):
        find("domains", domain=out["domain"], domain_type="l3dom")
    for node in model.get("l3out_nodes", []):
        ipv4(node["router_id"])
    for subnet in model.get("external_subnets", []):
        ipv4(subnet["network"], network=True)
    for route in model.get("static_routes", []):
        ipv4(route["prefix"], network=True)
        if not any(all(str(hop[k]) == str(route[source]) for k, source in
                       [("tenant", "tenant"), ("l3out", "l3out"), ("node_profile", "logical_node"),
                        ("pod_id", "pod_id"), ("node_id", "node_id"), ("prefix", "prefix")])
                   for hop in model.get("static_nexthops", [])):
            raise ValueError("Every static route needs at least one next hop")
    for hop in model.get("static_nexthops", []):
        address = ipv4(hop["nexthop"])
        candidate_interfaces = [i for i in model.get("l3out_interfaces", []) if all(
            str(i[f]) == str(hop[f]) for f in ("tenant", "l3out", "node_profile", "pod_id", "node_id")
        )]
        reachable = False
        for interface in candidate_interfaces:
            local = ipv4(interface["address"], interface=True)
            if address in local.network and address != local.ip:
                if local.network.prefixlen >= 31 or address not in (local.network.network_address, local.network.broadcast_address):
                    reachable = True
        if not reachable:
            raise ValueError("Static next hop must be a usable directly connected IPv4 peer")
    return model


def snapshot_data(results):
    """Keep APIC configuration only; never serialize authentication/module invocation."""
    return [{"path": item["item"], "imdata": item["imdata"]} for item in results]


def snapshot_paths(model):
    suffix = ".json?rsp-subtree=full&rsp-prop-include=config-only"
    paths = [f'/api/mo/uni/tn-{tenant["tenant"]}{suffix}' for tenant in model["tenants"]]
    access_sections = list(RESOURCES)[1:16]
    if any(model.get(section) for section in access_sections):
        paths.append(f"/api/mo/uni/infra{suffix}")
    paths.extend(f'/api/mo/uni/{domain["domain_type"]}-{domain["domain"]}{suffix}'
                 for domain in model.get("domains", []))
    return paths


def report_data(results, section):
    """Allowlist report fields instead of serializing the entire module result."""
    fields = ("changed", "previous", "current", "proposed")
    identity = RESOURCES[section]["identity"]
    return [dict({key: result[key] for key in fields if key in result},
                 section=section,
                 identity={key: result["item"][key] for key in identity})
            for result in results if not result.get("skipped", False)]


class FilterModule:
    def filters(self):
        return {"aci_load_model": load_model, "aci_snapshot_data": snapshot_data,
                "aci_report_data": report_data, "aci_snapshot_paths": snapshot_paths}
