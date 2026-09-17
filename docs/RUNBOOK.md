# Operations runbook

## Before a production change

1. Complete [acceptance testing](ACCEPTANCE.md) for the exact controller and APIC versions.
2. Record the intended Git commit, model checksum, target fabric, object ownership and traffic impact.
3. Confirm APIC cluster health, leaf registration, relevant access policies, interface availability,
   CA trust, account permissions and upstream routing. Check for objects managed by other systems.
4. Take a supported APIC configuration export using your established backup system. Verify the export
   completed, is available outside APIC, and has a tested restore procedure. Record its reference.
5. Obtain the appropriate change approval and schedule a maintenance window where needed. Use one
   operator or central job lock for a fabric; preserve management access independent of the affected path.
6. Run offline validation and a live plan. Review the incremental private report, including changes to
   existing objects. A plan with an error or without the `COMPLETED` marker is incomplete.

## Authentication

Password mode requires `ACI_USERNAME` and `ACI_PASSWORD`. Certificate mode requires
`ACI_USERNAME`, `ACI_PRIVATE_KEY` (absolute local PEM private-key path) and
`ACI_CERTIFICATE_NAME` (the certificate registered on the APIC account). Unset `ACI_PASSWORD`
when using certificate mode. Use a dedicated account, not a shared administrator identity.

Keep the key readable only by the automation user. Configure the APIC account certificate using
your existing identity-management process. This repository does not create accounts or keys.
Install the APIC issuing CA chain in the controller's operating-system trust store. TLS validation
and HTTPS are always enabled; the model cannot disable either. A trust or name mismatch must be
fixed at its source. Proxy use is disabled for direct fabric management.

## Plan, capture, apply and verify

The supported entry point is `python scripts/run.py`. All paths below are relative to the root.

```bash
python scripts/validate.py config/production.yml
python scripts/run.py plan --inventory inventory/production/hosts.yml --model config/production.yml
python scripts/run.py snapshot --inventory inventory/production/hosts.yml --model config/production.yml

python scripts/run.py apply --inventory inventory/production/hosts.yml --model config/production.yml \
  --change-id CHG-12345 --recovery-reference 'Verified external APIC export BACKUP-12345'

python scripts/run.py verify --inventory inventory/production/hosts.yml --model config/production.yml
```

Use real approved references. The wrapper prevents concurrent runs for the same APIC DNS name
on the same controller and OS account. It does not coordinate different accounts, controllers,
APIC aliases, direct playbook invocations or other automation tools. A central scheduler must
serialize all writers to a fabric. Inventory must select exactly one APIC endpoint, not one entry
per APIC cluster member. All relevant APIC firmware records must match the model allowlist.

`site.yml` defaults to check mode. Explicit `aci_apply=true` enables writes; CLI `--check` continues
to prevent configuration writes even when that flag is provided. Do not use tags, `--start-at-task`,
or edited guards to bypass preflight and dependency ordering. The wrapper exposes no such options.

During apply, the workflow captures selected configuration before the first managed configuration
write. Tenant-only models capture their managed tenants. Access models additionally capture
`uni/infra` and their physical/L3 domains. Files are stored with mode 0600 in private mode 0700
directories. Capture failure stops deployment. A large fabric may require a reviewed timeout
adjustment in module defaults.

These JSON captures are **diagnostic configuration snapshots**, not complete APIC backups.
They can omit secrets, system state and unmanaged roots. They must not be blindly POSTed back to APIC.
Module invocation/authentication data is excluded, but configuration itself remains sensitive.

The incremental `report.json` is updated after each successful resource section. If a module fails,
the failing section may have partially changed APIC and may not appear in the report. Absence of
`COMPLETED` means the workflow did not finish. `COMPLETED` records workflow completion only.
Protect and retain reports with the approved change record; never publish them in public CI artifacts.

## Verification and drift

Verification performs the same reconciliation in check mode and fails at the first changed resource
section. It then checks critical/major faults under managed tenants. It can fail on pre-existing
faults, and it does not check all fabric-wide faults or prove data-plane health.

After the fabric converges, run verification, inspect APIC's operational status, and test:

- Intended allowed and denied contract traffic, including reverse flows.
- Endpoint learning, domain deployment, interface state and VLAN encapsulation.
- L3Out adjacencies/routes, external return routes and expected route advertisement.
- The redundancy and failover scenarios in your actual topology.

A second apply in the lab should show zero configuration changes. Artifact creation is expected
to count as changed in the Ansible recap; use the per-object `changed` fields in `report.json`
for configuration idempotency. Model verification covers desired managed settings only.

## Failure and recovery

Ansible/APIC updates are not atomic across tasks and there is no automatic rollback. On failure,
stop other writers, record the last completed section, inspect APIC faults/audit events and compare
the captured state with the intended change. Console module results are intentionally hidden;
use APIC diagnostics and private reports for investigation. Do not upload verbose logs publicly.

If the intended state is still correct and the failure was transient, fix the cause, plan again,
and resume with a full run. There are no blind retries for configuration writes.

If a previous configuration must be restored, use the tested, release-specific APIC recovery
procedure and external backup under an approved recovery change. A Git revert followed by apply
can restore explicitly managed attributes, but **cannot remove newly created objects** or fully
undo removed declarations. Restoring a whole APIC export can overwrite unrelated changes;
coordinate scope with the fabric owner. Deletion needs a separate reviewed, dependency-ordered
procedure, usually relationships and children before parents.

## Dependency maintenance

Python dependencies and the Cisco collection are pinned. `constraints.txt` records a complete
version resolution but is not a hash-verified package mirror. Use your organization's approved
artifact repository or hash-locked packages if required. Update pins together, run CI and lab
acceptance, and record the new baseline before production use. Dependabot does not update the
Galaxy collection automatically; maintain `collections/requirements.yml` explicitly.
