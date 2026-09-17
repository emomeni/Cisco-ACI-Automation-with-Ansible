# Validation evidence

Prepared on **2026-09-17** for release **0.1.0**.

## Completed in the preparation environment

| Check | Result |
| --- | --- |
| Python behavioral and workflow tests | **65 passed** |
| Tenant-only example | Valid; 12 managed objects |
| Full-stack example | Valid; 44 managed objects across 40 sections |
| Collection parameter checks | **40 modules passed** against Cisco ACI 2.13.0 source |
| Python source compilation | Passed |
| YAML formatting | Passed after normalization to LF line endings |
| Direct Python dependency resolution | Exact requested versions resolved successfully |
| Workflow security assertions | Read-only permissions, pinned actions, no APIC secrets or deployment in CI |

Tests include rejection of protected tenants, undeclared references, unsupported settings,
unknown keys, credential overrides, duplicate identities, invalid VLAN and transport ranges,
overlapping subnets/selectors, conflicting paths, unusable next hops and embedded templates.
They also check private-report field selection, snapshot path coverage and CLI check-mode precedence.

The collection check compares checked-in task parameters to both documentation metadata and
runtime argument names in the exact release source. It checks declared check-mode support and
the schema's selected enum values. It does not execute modules against an APIC.

## Pending qualification

| Check | Status and reason |
| --- | --- |
| Linux Ansible syntax checks | Pending; the preparation session is Windows and could not access a Linux controller |
| GitHub Actions execution | Pending publication; workflow included, not claimed to have run |
| Dependency installation on the intended Linux controller | Pending; local dependency resolution used Windows/Python 3.12 |
| Live APIC create/update/query behavior | Pending; no APIC address, credentials or fabric supplied |
| Live check-mode safety and idempotency | Pending; requires the target APIC release |
| Contract traffic, routing, fault convergence and failover | Pending; requires the actual topology |
| Backup restoration | Pending; requires the site's supported APIC backup process |
| Site-specific RBAC and operational approval | Pending; owned by the fabric operator |

The APIC version in the examples is illustrative. There is no certified APIC compatibility
matrix or claim that every ACI feature is supported. Run `make check` on Linux, then complete
[ACCEPTANCE.md](ACCEPTANCE.md) before a production rollout.

This repository provides production-oriented controls and documentation. It cannot be described
as fully production validated until those environment-specific checks have passed.
