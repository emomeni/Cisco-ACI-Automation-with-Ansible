# Site acceptance record

Complete and retain a copy in your private change records. An unchecked item is not a passed test.

| Field | Site evidence |
| --- | --- |
| Repository commit and model checksum | |
| Python, ansible-core and cisco.aci versions | |
| Exact APIC versions for every controller | |
| Leaf/spine models and software versions | |
| Reviewed topology, VLANs, VRFs, contracts and ownership | |
| Test date, reviewer and change reference | |
| External APIC backup and tested restore evidence | |

- [ ] `make check` passes on the intended Linux controller, including Ansible syntax checks.
- [ ] Wrong credentials, invalid certificate trust, wrong target and disallowed firmware fail before writes.
- [ ] No credentials appear in console output, reports, snapshots or source control.
- [ ] A new isolated tenant and its resources can be created using this exact code and model.
- [ ] A controlled setting update produces the intended APIC change and no unexpected changes.
- [ ] A second apply reports zero managed-object changes; verification passes after convergence.
- [ ] A deliberate manual change is detected by verification and safely reconciled after review.
- [ ] Check mode produces no APIC configuration changes, including on a new/empty tenant.
- [ ] Planned failure halfway through a lab run is diagnosed and recovered using the runbook.
- [ ] Leaf selection, AEP/domain/VLAN relationships and endpoint deployment match the physical topology.
- [ ] Allowed and denied contract flows behave correctly; upstream routing provides return reachability.
- [ ] Redundancy/failure behavior is tested for the site's design; the supplied one-leaf example is not used as an HA design.
- [ ] The external APIC backup restore has been rehearsed on a compatible lab target.
- [ ] One-writer coordination, permissions, monitoring, audit retention and support ownership are assigned.
- [ ] Existing unrelated objects and automation ownership were reviewed before adoption.
- [ ] Production go/no-go is approved by the fabric owner after reviewing this evidence.
