# Contributing

Open a sanitized issue explaining the intended ACI behavior, affected module and APIC release.
For changes, use a branch and pull request with the supplied template. Run `make check` from a
Linux controller. Never include credentials, customer configuration or private audit artifacts.

Keep schema, resource registry, validator, role tasks, examples and documentation aligned.
Tests should exercise meaningful failure boundaries and supported behavior. For runtime changes,
record create/update/idempotency/check-mode results and data-plane checks on an actual lab APIC.
Label untested behavior explicitly. Do not describe offline-only changes as production certified.

Maintain `CHANGELOG.md`. Dependency upgrades should be separate, reviewed changes with a new
compatibility record. Original contributions use the repository's MIT license; do not copy
third-party collection code into this repository without an appropriate license review.
