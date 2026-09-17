# Implemented resources

The schema intentionally narrows module options to the supported design in this repository. Collection version: **2.13.0**. No claim is made to implement every ACI feature.

| Model section | Collection module | Upstream documentation |
| --- | --- | --- |
| `tenants` | `aci_tenant` | [aci_tenant](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_tenant_module.html) |
| `vlan_pools` | `aci_vlan_pool` | [aci_vlan_pool](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_vlan_pool_module.html) |
| `vlan_blocks` | `aci_vlan_pool_encap_block` | [aci_vlan_pool_encap_block](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_vlan_pool_encap_block_module.html) |
| `domains` | `aci_domain` | [aci_domain](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_domain_module.html) |
| `domain_pools` | `aci_domain_to_vlan_pool` | [aci_domain_to_vlan_pool](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_domain_to_vlan_pool_module.html) |
| `aeps` | `aci_aep` | [aci_aep](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_aep_module.html) |
| `aep_domains` | `aci_aep_to_domain` | [aci_aep_to_domain](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_aep_to_domain_module.html) |
| `lldp_policies` | `aci_interface_policy_lldp` | [aci_interface_policy_lldp](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_interface_policy_lldp_module.html) |
| `cdp_policies` | `aci_interface_policy_cdp` | [aci_interface_policy_cdp](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_interface_policy_cdp_module.html) |
| `link_policies` | `aci_interface_policy_link_level` | [aci_interface_policy_link_level](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_interface_policy_link_level_module.html) |
| `access_policy_groups` | `aci_interface_policy_leaf_policy_group` | [aci_interface_policy_leaf_policy_group](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_interface_policy_leaf_policy_group_module.html) |
| `interface_profiles` | `aci_interface_policy_leaf_profile` | [aci_interface_policy_leaf_profile](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_interface_policy_leaf_profile_module.html) |
| `access_ports` | `aci_access_port_to_interface_policy_leaf_profile` | [aci_access_port_to_interface_policy_leaf_profile](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_access_port_to_interface_policy_leaf_profile_module.html) |
| `leaf_profiles` | `aci_switch_policy_leaf_profile` | [aci_switch_policy_leaf_profile](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_switch_policy_leaf_profile_module.html) |
| `leaf_selectors` | `aci_switch_leaf_selector` | [aci_switch_leaf_selector](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_switch_leaf_selector_module.html) |
| `leaf_interfaces` | `aci_interface_selector_to_switch_policy_leaf_profile` | [aci_interface_selector_to_switch_policy_leaf_profile](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_interface_selector_to_switch_policy_leaf_profile_module.html) |
| `vrfs` | `aci_vrf` | [aci_vrf](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_vrf_module.html) |
| `bridge_domains` | `aci_bd` | [aci_bd](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_bd_module.html) |
| `subnets` | `aci_bd_subnet` | [aci_bd_subnet](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_bd_subnet_module.html) |
| `applications` | `aci_ap` | [aci_ap](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_ap_module.html) |
| `epgs` | `aci_epg` | [aci_epg](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_epg_module.html) |
| `filters` | `aci_filter` | [aci_filter](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_filter_module.html) |
| `filter_entries` | `aci_filter_entry` | [aci_filter_entry](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_filter_entry_module.html) |
| `contracts` | `aci_contract` | [aci_contract](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_contract_module.html) |
| `subjects` | `aci_contract_subject` | [aci_contract_subject](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_contract_subject_module.html) |
| `subject_filters` | `aci_contract_subject_to_filter` | [aci_contract_subject_to_filter](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_contract_subject_to_filter_module.html) |
| `epg_contracts` | `aci_epg_to_contract` | [aci_epg_to_contract](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_epg_to_contract_module.html) |
| `l3outs` | `aci_l3out` | [aci_l3out](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_l3out_module.html) |
| `l3out_node_profiles` | `aci_l3out_logical_node_profile` | [aci_l3out_logical_node_profile](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_l3out_logical_node_profile_module.html) |
| `l3out_nodes` | `aci_l3out_logical_node` | [aci_l3out_logical_node](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_l3out_logical_node_module.html) |
| `l3out_interface_profiles` | `aci_l3out_logical_interface_profile` | [aci_l3out_logical_interface_profile](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_l3out_logical_interface_profile_module.html) |
| `l3out_interfaces` | `aci_l3out_interface` | [aci_l3out_interface](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_l3out_interface_module.html) |
| `static_routes` | `aci_l3out_static_routes` | [aci_l3out_static_routes](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_l3out_static_routes_module.html) |
| `static_nexthops` | `aci_l3out_static_routes_nexthop` | [aci_l3out_static_routes_nexthop](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_l3out_static_routes_nexthop_module.html) |
| `external_epgs` | `aci_l3out_extepg` | [aci_l3out_extepg](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_l3out_extepg_module.html) |
| `external_subnets` | `aci_l3out_extsubnet` | [aci_l3out_extsubnet](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_l3out_extsubnet_module.html) |
| `external_contracts` | `aci_l3out_extepg_to_contract` | [aci_l3out_extepg_to_contract](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_l3out_extepg_to_contract_module.html) |
| `bd_l3outs` | `aci_bd_to_l3out` | [aci_bd_to_l3out](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_bd_to_l3out_module.html) |
| `epg_domains` | `aci_epg_to_domain` | [aci_epg_to_domain](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_epg_to_domain_module.html) |
| `static_bindings` | `aci_static_binding_to_epg` | [aci_static_binding_to_epg](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/aci_static_binding_to_epg_module.html) |
