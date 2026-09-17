# Cisco ACI Automation with Ansible

Intent-driven automation framework for deploying, validating, and verifying Cisco ACI configuration through the APIC API using Ansible and the `cisco.aci` collection.

This repository is designed around a simple principle:

> Network changes should be validated before deployment, applied in a controlled way, and verified afterward.

The project focuses on Cisco ACI tenant networking, contracts, access policies, EPG bindings, and static-routing L3Out configuration while adding validation, change planning, verification, and operational safeguards around the automation workflow.

---

## Overview

The repository provides a structured workflow for managing Cisco ACI configuration as code:

```text
Intent YAML
     │
     ▼
Schema Validation
     │
     ▼
Dependency & Consistency Validation
     │
     ▼
Ansible + cisco.aci
     │
     ▼
Plan / Check Mode
     │
     ▼
Apply
     │
     ▼
Verify / Drift / Fault Checks
```

The goal is not simply to execute Ansible modules against APIC.

The goal is to build a safer automation workflow around those modules.

---

## Key Features

- Intent-driven Cisco ACI configuration
- Cisco `cisco.aci` Ansible collection
- Strict JSON Schema validation
- Duplicate and dependency validation
- Network consistency checks
- Plan-before-apply workflow
- Explicit apply mode
- Post-deployment verification
- Configuration snapshot capability
- Tenant fault checks
- Drift detection
- Structured execution reports
- Secure credential injection
- Mandatory TLS verification
- Lab and production inventory separation
- Reusable Ansible roles
- Automated tests
- GitHub Actions CI
- Dependabot dependency monitoring
- Operational runbook and acceptance guidance

---

## Project Status

Current release:

```text
v0.1.x
```

The project is suitable for:

- Cisco ACI labs
- automation testing
- learning and experimentation
- proof-of-concept environments
- controlled evaluation

Before using the project in production, validate it against:

- your APIC release
- your leaf/spine hardware
- your network design
- your organizational change process
- your recovery procedures

Offline validation and successful Ansible execution do not guarantee compatibility with every ACI deployment.

See:

- [`docs/VALIDATION.md`](docs/VALIDATION.md)
- [`docs/ACCEPTANCE.md`](docs/ACCEPTANCE.md)
- [`docs/RUNBOOK.md`](docs/RUNBOOK.md)

---

## Supported ACI Design

| Area | Implemented |
|---|---|
| Tenant networking | Tenants, VRFs, Bridge Domains, IPv4 gateways |
| Application networking | Application Profiles and EPGs |
| Contracts | Filters, subjects, providers and consumers |
| Access policies | VLAN pools, domains, AEPs and interface policy objects |
| Interface configuration | Standalone leaf ports, selectors and interface profiles |
| EPG attachments | Physical domains and static path bindings |
| L3Out | Routed interfaces, node/interface profiles and static routes |
| External connectivity | External EPGs, external subnets and contract relations |
| Validation | Schema, dependency and consistency validation |
| Operations | Snapshot, plan, apply, verify and reporting |

The implementation is intentionally bounded and is not intended to expose every feature available through Cisco ACI.

---

## Currently Out of Scope

- fabric discovery
- APIC cluster bootstrap
- switch registration
- vPC
- port channels
- VMM integration
- BGP-based L3Out
- OSPF-based L3Out
- IPv6
- ESGs
- service graphs
- AAA configuration
- firmware upgrades
- Multi-Pod
- Multi-Site
- automatic deletion workflows

These features should be designed, implemented, and tested separately before being added.

---

## Architecture

Ansible runs from the control node and communicates directly with the APIC API over HTTPS.

```text
                  ┌──────────────────────┐
                  │    Intent YAML       │
                  │  config / examples   │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Validation Layer     │
                  │ JSON Schema          │
                  │ Dependencies         │
                  │ Consistency Checks   │
                  └──────────┬───────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ Ansible Controller   │
                  │ Playbooks            │
                  │ Roles                │
                  │ cisco.aci            │
                  └──────────┬───────────┘
                             │
                          HTTPS
                             │
                             ▼
                  ┌──────────────────────┐
                  │      Cisco APIC      │
                  └──────────┬───────────┘
                             │
                             ▼
                     Cisco ACI Fabric
```

Ansible does not SSH directly to the ACI leaf switches. Configuration is performed through APIC.

---

## Requirements

Recommended control-node environment:

- Linux
- Python 3.12
- Ansible Core
- Cisco `cisco.aci` collection
- HTTPS connectivity to APIC
- trusted APIC CA certificates

Current tested baseline:

```text
Python:       3.12
ansible-core: 2.20.x
cisco.aci:    2.13.x
```

Exact dependency constraints are maintained in:

```text
constraints.txt
requirements.txt
requirements-dev.txt
collections/requirements.yml
```

Always review dependency updates before using them in production.

---

## Repository Structure

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   ├── dependabot.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── collections/
│   └── requirements.yml
├── config/
│   └── README.md
├── docs/
│   ├── ACCEPTANCE.md
│   ├── MODEL.md
│   ├── MODULES.md
│   ├── RUNBOOK.md
│   ├── SOURCES.md
│   └── VALIDATION.md
├── examples/
│   ├── full-stack.yml
│   └── tenant-only.yml
├── filter_plugins/
│   └── aci_model.py
├── inventory/
│   ├── lab/
│   │   └── hosts.yml
│   └── production/
│       └── hosts.yml
├── playbooks/
│   ├── tasks/
│   ├── site.yml
│   ├── snapshot.yml
│   └── verify.yml
├── roles/
│   ├── aci_access/
│   ├── aci_bindings/
│   ├── aci_contracts/
│   ├── aci_l3out/
│   ├── aci_network/
│   └── aci_tenants/
├── schemas/
│   ├── aci.schema.json
│   └── resources.json
├── scripts/
│   ├── check_collection.py
│   ├── run.py
│   └── validate.py
├── tests/
├── .env.example
├── .gitignore
├── .python-version
├── .yamllint.yml
├── ansible.cfg
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── NOTICE
├── README.md
├── SECURITY.md
├── constraints.txt
├── pytest.ini
├── requirements.txt
└── requirements-dev.txt
```

---

## Installation

```bash
git clone https://github.com/emomeni/Cisco-ACI-Automation-with-Ansible.git
cd Cisco-ACI-Automation-with-Ansible

python3.12 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt -c constraints.txt

ansible-galaxy collection install \
  -r collections/requirements.yml \
  -p .ansible/collections

make check
```

---

## Prepare a Lab Configuration

```bash
cp examples/full-stack.yml config/lab.yml
```

Then customize `config/lab.yml` for your environment.

Typical values to review include:

- APIC hostname
- APIC version allowlist
- tenant names
- VRFs
- Bridge Domains
- VLAN IDs
- node IDs
- interface IDs
- subnet addressing
- L3Out parameters
- static routes
- next-hop addresses

The configuration under `config/` is ignored by Git by default.

---

## Inventory

Example lab inventory:

```yaml
---
all:
  children:
    apic:
      hosts:
        lab_apic:
          aci_host: apic.lab.example.com
          aci_environment: lab
          aci_model_file: "{{ playbook_dir }}/../examples/full-stack.yml"
```

Replace the example hostname with your actual APIC FQDN.

Do not commit real customer or production inventory information to a public repository.

---

## Credentials

Credentials must not be stored in YAML files.

```bash
export ACI_USERNAME=automation

read -rsp 'APIC password: ' ACI_PASSWORD
printf '\n'
export ACI_PASSWORD
```

Certificate authentication can also be used where appropriate.

The repository intentionally excludes:

```text
.env
*.key
*.pem
*.p12
*.pfx
*vault*.yml
config/*
artifacts/
```

Never commit:

- APIC passwords
- API credentials
- private keys
- customer inventory
- production intent files
- configuration exports
- snapshots
- execution reports containing sensitive topology data

---

## TLS Verification

TLS certificate validation should remain enabled.

Install the APIC CA certificate into the trust store of the automation controller.

Do not disable certificate verification simply to bypass certificate errors.

---

## Workflow

```text
Validate
   ↓
Plan
   ↓
Review
   ↓
Snapshot
   ↓
Apply
   ↓
Verify
   ↓
Operational Testing
```

### 1. Validate

```bash
python scripts/validate.py config/lab.yml
```

### 2. Plan

```bash
python scripts/run.py plan \
  --inventory inventory/lab/hosts.yml \
  --model config/lab.yml
```

### 3. Apply

```bash
python scripts/run.py apply \
  --inventory inventory/lab/hosts.yml \
  --model config/lab.yml \
  --change-id LAB-001 \
  --recovery-reference "Verified APIC backup before LAB-001"
```

### 4. Verify

```bash
python scripts/run.py verify \
  --inventory inventory/lab/hosts.yml \
  --model config/lab.yml
```

---

## Snapshot

```bash
ansible-playbook \
  -i inventory/lab/hosts.yml \
  playbooks/snapshot.yml
```

Snapshots should be stored securely and should not be committed to a public repository.

---

## Main Playbooks

### `playbooks/site.yml`
Primary configuration reconciliation workflow.

### `playbooks/verify.yml`
Post-deployment verification workflow.

### `playbooks/snapshot.yml`
Collects relevant APIC configuration information before a change.

---

## Roles

### `aci_tenants`

Tenant-level resources such as tenants, VRFs, Bridge Domains, application profiles, and EPGs.

### `aci_access`

Physical access policy configuration such as VLAN pools, domains, AEPs, interface policies, selectors, and interface profiles.

### `aci_network`

Network objects and connectivity relationships.

### `aci_contracts`

Cisco ACI contracts including filters, filter entries, subjects, provider relationships, and consumer relationships.

### `aci_l3out`

Static-routing L3Out automation including node profiles, interface profiles, routed interfaces, static routes, next hops, external EPGs, and external subnets.

### `aci_bindings`

EPG and infrastructure bindings including static path relationships.

---

## Intent Model

The YAML files under `examples/` demonstrate the supported intent model:

```text
examples/tenant-only.yml
examples/full-stack.yml
```

The full-stack example demonstrates relationships between:

```text
Tenant
   │
   ├── VRF
   ├── Bridge Domain
   ├── Application Profile
   │       └── EPG
   ├── Contracts
   ├── Physical Domain
   ├── Static Path
   └── L3Out
```

The full-stack example is intentionally simple and should not be interpreted as a production HA architecture.

---

## Validation Layer

Validation includes:

```text
YAML
 ↓
JSON Schema
 ↓
Object validation
 ↓
Reference validation
 ↓
Dependency validation
 ↓
Network consistency checks
 ↓
Ansible
```

Relevant files:

```text
schemas/aci.schema.json
schemas/resources.json
filter_plugins/aci_model.py
scripts/validate.py
```

---

## Testing

```bash
pytest
```

Or run the complete project checks:

```bash
make check
```

Tests do not replace validation against a real APIC environment.

---

## Continuous Integration

GitHub Actions performs offline repository validation.

The workflow does not connect to APIC and does not require APIC credentials.

Typical CI checks include:

```text
YAML validation
Python tests
schema validation
repository checks
collection/module compatibility checks
```

Public pull requests should never receive production APIC credentials.

---

## Dependency Management

Dependencies are managed through:

```text
requirements.txt
requirements-dev.txt
constraints.txt
collections/requirements.yml
```

Dependabot monitors selected dependencies and GitHub Actions.

Dependency updates should be reviewed and tested before merging.

---

## Operational Safety

Before running automation against production ACI:

1. Validate the intent model.
2. Review the generated plan.
3. Confirm APIC RBAC.
4. Confirm the target environment.
5. Capture a known-good configuration state.
6. Define a recovery procedure.
7. Verify the relevant change approval.
8. Apply the change.
9. Run post-deployment verification.
10. Validate application traffic.

Automation reduces repetitive work. It does not remove the need for operational discipline.

---

## Important Reconciliation Behavior

Removing an object from the YAML model does not automatically delete that object from APIC.

The current implementation primarily uses declarative `state: present` behavior.

See [`docs/MODEL.md`](docs/MODEL.md) for detailed reconciliation semantics.

---

## Production Usage

Before production adoption, complete the acceptance process described in:

[`docs/ACCEPTANCE.md`](docs/ACCEPTANCE.md)

At minimum, validate:

- supported APIC version
- module behavior
- leaf/interface references
- VLAN allocation
- tenant relationships
- contracts
- L3Out connectivity
- routing behavior
- rollback procedure
- application traffic

---

## Security

Please read:

[`SECURITY.md`](SECURITY.md)

Security recommendations include:

- dedicated APIC automation identities
- least-privilege RBAC
- external secret management
- trusted TLS certificates
- private configuration files
- private execution artifacts
- reviewed pull requests
- isolated CI from production APIC
- controlled dependency upgrades

---

## Documentation

- [`docs/MODEL.md`](docs/MODEL.md)
- [`docs/MODULES.md`](docs/MODULES.md)
- [`docs/RUNBOOK.md`](docs/RUNBOOK.md)
- [`docs/VALIDATION.md`](docs/VALIDATION.md)
- [`docs/ACCEPTANCE.md`](docs/ACCEPTANCE.md)
- [`docs/SOURCES.md`](docs/SOURCES.md)

---

## Contributing

Contributions are welcome.

Before submitting a pull request:

```bash
make check
```

Please ensure that:

- no credentials are included
- no customer data is included
- examples use sanitized values
- new modules are documented
- validation rules are updated when needed
- tests are included for behavioral changes
- documentation reflects new functionality

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Roadmap

Potential future additions include:

- vPC interface policy support
- port-channel support
- BGP L3Out
- OSPF L3Out
- IPv6
- VMM integration
- ESG automation
- enhanced drift detection
- explicit deletion workflows
- rollback orchestration
- CI-based intent policy checks
- source-of-truth integration
- NetBox integration
- GitOps deployment workflows

---

## License

The original code in this repository is distributed under the MIT License.

See [`LICENSE`](LICENSE).

The separately installed `ansible-core` and Cisco `cisco.aci` collection retain their respective licenses.

See [`NOTICE`](NOTICE).

---

## Disclaimer

This is an independent community project.

It is not an official Cisco or Red Hat product and is not endorsed by Cisco or Red Hat.

Always validate automation against your specific environment before production deployment.

---

## Author

**Ehsan Momeni**  
Network Automation Consultant

GitHub:  
https://github.com/emomeni

Repository:  
https://github.com/emomeni/Cisco-ACI-Automation-with-Ansible

---

If you find this repository useful, consider giving it a ⭐ and sharing feedback through GitHub Issues or Pull Requests.
