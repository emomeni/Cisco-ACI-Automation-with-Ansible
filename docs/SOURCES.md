# Upstream references

Verified on 2026-09-17. The repository uses these projects as separately installed dependencies.

- [Cisco ACI collection source](https://github.com/CiscoDevNet/ansible-aci), release
  [v2.13.0](https://github.com/CiscoDevNet/ansible-aci/releases/tag/v2.13.0), commit
  `d6a5c3f6f5192023121ecd304ef140a768bfcdc9`.
- [Official collection documentation](https://docs.ansible.com/projects/ansible/latest/collections/cisco/aci/index.html).
  Per-resource module references are listed in [MODULES.md](MODULES.md).
- [ansible-core 2.20.9 distribution](https://pypi.org/project/ansible-core/2.20.9/).
- [Ansible check and diff modes](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html).
- [Ansible control-node requirements](https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_installation.html).
- [Cisco ACI product documentation](https://www.cisco.com/c/en/us/support/cloud-systems-management/application-policy-infrastructure-controller-apic/series.html).

Use your APIC release's configuration, backup/restore and security documentation when completing
site acceptance. Collection support does not imply that every module option works on every APIC version.
