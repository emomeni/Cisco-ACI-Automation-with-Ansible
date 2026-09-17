# Security policy

Report vulnerabilities privately using GitHub private vulnerability reporting when enabled.
The repository owner must enable this feature or publish a monitored private security contact
before accepting reports. Do not post secrets, fabric exports or exploitable customer details in issues.

The initial release has no promised maintenance SLA. Maintainers should triage reports, assess
affected versions and publish fixes with clear upgrade instructions.

## Operational boundaries

- Treat repository code, custom filters and inventory as trusted executable inputs. Review changes before running with APIC credentials.
- Store credentials in a secret manager and inject them at runtime. The model accepts no passwords or arbitrary module overrides.
- Use dedicated APIC identities with the smallest practical permissions. Tenant-only models require tenant management plus firmware-query access;
  access-policy management also needs the relevant infrastructure permissions. Confirm the exact RBAC scope on your APIC release.
- Keep HTTPS verification enabled and trust the APIC CA on the controller. Do not disable certificate checks to resolve connectivity errors.
- Keep private keys, actual inventory data, intent, reports and snapshots out of public repositories. Git ignore rules are a convenience, not a secret scanner.
- Limit access to the controller: environment secrets may be observable by privileged users or processes running as the same user.
- GitHub CI runs no APIC operations and receives no APIC credentials. Do not expose a privileged self-hosted controller to untrusted pull requests.
- CI actions use immutable commit references and read-only repository permissions. Dependency updates require review and lab testing.

The workflow's change/recovery references and local process lock support operations; they are not
authorization systems. APIC RBAC, organizational approvals and central job coordination remain required.
