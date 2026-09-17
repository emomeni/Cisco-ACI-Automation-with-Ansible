# Cisco ACI configuration with Ansible

An intent-driven repository for configuring Cisco ACI tenants, physical access policies,
contracts, EPG attachments and IPv4 static-routing L3Outs through the APIC API.

**Release 0.1.0 — ready for GitHub publication and lab qualification. Production acceptance
is pending.** Offline validation is not proof of compatibility with your APIC release,
switch hardware or traffic design. See [validation evidence](docs/VALIDATION.md) before deployment.

## Included

- Six ordered roles covering **40 resource types** using `cisco.aci` modules.
- Tenant-only and complete physical-access/L3Out examples, plus separate lab and production inventories.
- Strict JSON Schema, duplicate-key rejection, dependency checks and network consistency validation.
- Check mode by default; explicit apply mode with change and recovery references.
- Mandatory TLS verification, password or certificate authentication, and private audit files.
- Configuration capture before apply, drift verification, tenant fault checks and an operations runbook.
- Behavioral tests, module parameter checks, GitHub Actions CI, dependency updates and MIT licensing.

## Supported design

| Area | Implemented |
| --- | --- |
| Tenant network | Tenants, enforced VRFs, BDs, IPv4 gateways, application profiles, EPGs |
| Contracts | TCP/UDP port filters, bidirectional subjects, provider/consumer relations |
| Access | Static VLAN pools, physical/L3 domains, AEPs, LLDP/CDP/link policies, standalone leaf ports, selectors and profiles |
| Attachments | Physical EPG domains and single-leaf static paths, including VLAN validation |
| L3Out | Routed physical ports, node/interface profiles, IPv4 static routes and next hops, external EPGs/subnets/contracts, BD associations |

This is an intentionally bounded implementation, not every feature in the Cisco collection.
Fabric discovery/bootstrap, APIC clustering, switch registration, vPC/port channels, VMM,
BGP/OSPF, IPv6, ESGs, service graphs, AAA, firmware upgrades, Multi-Pod/Multi-Site orchestration
and deletion workflows require separately designed and tested extensions.
The full-stack example uses one leaf and one uplink to make the relationships readable;
it is **not a redundant production topology**. Hardware and upstream router configuration
are prerequisites. [Module coverage](docs/MODULES.md) lists every implemented resource.

## Controller requirements

- A Linux control node with Python 3.12, outbound access for dependency installation, and HTTPS access to APIC.
- Pinned baseline: `ansible-core 2.20.9`, `cisco.aci 2.13.0`; remaining versions are constrained in `constraints.txt`.
- APIC CA certificates installed in the controller's trust store; DNS must match the server certificate.
- An APIC automation account authorized for the managed objects and controller firmware queries.
- An initialized fabric with the intended leaf IDs and working management connectivity.

Ansible runs locally on the controller and uses APIC HTTPS. It does not SSH into leaf switches.
Native Windows is not the Ansible control-node target; use a Linux VM or WSL2.
The sample APIC version `6.1(4a)` is an illustrative allowlist entry, **not a compatibility certification**.
Replace it with the exact versions validated for your site, including every controller in the cluster.

## Get started in a lab

Run commands from the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt -c constraints.txt
ansible-galaxy collection install -r collections/requirements.yml -p .ansible/collections
make check

cp examples/full-stack.yml config/lab.yml
```

Edit `config/lab.yml` and `inventory/lab/hosts.yml` for your lab. Replace the APIC DNS name,
version allowlist, tenant names, VLANs, node IDs, ports, addressing and upstream routes.
Keep the same `target.apic_host` and environment in the model and inventory.
The wrapper explicitly selects the model, overriding the inventory's example default.

Inject credentials from your secret manager, or enter a password without putting it in shell history:

```bash
export ACI_USERNAME=automation
read -rsp 'APIC password: ' ACI_PASSWORD; printf '\n'
export ACI_PASSWORD

python scripts/validate.py config/lab.yml
python scripts/run.py plan --inventory inventory/lab/hosts.yml --model config/lab.yml
```

Review the private `artifacts/aci-run-*/report.json` from that run. It contains object identities,
change flags and the collection's previous/current/proposed fields when returned. APIC credentials
and module invocation arguments are excluded. Plans are advisory: check mode cannot create missing
parents, validate switch behavior, reserve a configuration or guarantee a later apply.

After reviewing the model, plan and recovery procedure:

```bash
python scripts/run.py apply --inventory inventory/lab/hosts.yml --model config/lab.yml \
  --change-id LAB-001 --recovery-reference 'APIC backup: verified lab export before LAB-001'
python scripts/run.py verify --inventory inventory/lab/hosts.yml --model config/lab.yml
unset ACI_PASSWORD
```

These references are recorded for traceability; the repository cannot verify that an external
ticket was approved or a backup is restorable. Run traffic and recovery checks from
[the runbook](docs/RUNBOOK.md). For production, use `config/production.yml`, the production
inventory and your approved design after completing [acceptance testing](docs/ACCEPTANCE.md).

## Repository layout

```text
.github/             CI, dependency updates, issue and PR templates
collections/         Pinned Cisco ACI collection requirement
config/              Ignored private configuration files
docs/                Model guide, operations, security, acceptance and evidence
examples/            Sanitized runnable intent examples
filter_plugins/      Offline intent and report filters
inventory/           Lab and production APIC inventory templates
playbooks/           Reconciliation, verification and snapshot workflows
roles/               Tenant, access, network, contract, L3Out and binding tasks
schemas/             Strict intent schema and resource registry
scripts/             Validator, workflow wrapper and collection checks
tests/               Offline behavioral and workflow tests
```

Removing an object from YAML does **not** delete it from APIC. Likewise, `state: present` can
change existing settings and disrupt traffic. See [ownership and reconciliation semantics](docs/MODEL.md).
No public GitHub workflow connects to APIC. CI validates code and examples only.

## Publish to GitHub

The ZIP contains the repository contents, including hidden GitHub configuration, without a Git
history or downloaded dependencies. Extract it, create an empty repository in your GitHub account,
and review the files before the first commit:

```bash
git init -b main
git add .
git diff --cached --stat
git diff --cached
git commit -m "Initial ACI Ansible automation repository"
git remote add origin https://github.com/YOUR-ACCOUNT/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your own. Enable branch protection, require the `validate` CI job,
add maintainers as code owners, enable private vulnerability reporting, and review automated
dependency updates. Add an actual security contact if private reporting is unavailable.
These GitHub settings cannot be activated by files in a ZIP.

MIT applies to the original repository. Separately installed Ansible and Cisco collection
dependencies retain their own licenses; see [NOTICE](NOTICE).
