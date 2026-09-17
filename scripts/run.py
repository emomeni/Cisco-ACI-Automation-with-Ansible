#!/usr/bin/env python3
"""Run the repository workflow with one local lock per APIC DNS name."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "filter_plugins"))
from aci_model import load_model  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["plan", "apply", "verify", "snapshot"])
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--change-id")
    parser.add_argument("--recovery-reference")
    args = parser.parse_args()
    if os.name != "posix":
        parser.error("Run Ansible from a supported Linux controller, including a Linux VM or WSL2")
    import fcntl

    inventory = args.inventory.resolve(strict=True)
    model_path = args.model.resolve(strict=True)
    model = load_model(model_path.read_text(encoding="utf-8"))
    if args.operation == "apply" and not (args.change_id and args.recovery_reference):
        parser.error("Apply requires --change-id and --recovery-reference; see docs/RUNBOOK.md")
    lock_root = Path(tempfile.gettempdir()) / f"aci-ansible-{os.getuid()}"
    lock_root.mkdir(mode=0o700, exist_ok=True)
    key = hashlib.sha256(model["target"]["apic_host"].lower().encode()).hexdigest()
    extra = {"aci_model_file": str(model_path), "aci_apply": args.operation == "apply",
             "aci_verify": args.operation == "verify",
             "aci_change_id": args.change_id or "", "aci_recovery_reference": args.recovery_reference or ""}
    playbook = "snapshot.yml" if args.operation == "snapshot" else "site.yml"
    command = ["ansible-playbook", "-i", str(inventory), str(ROOT / "playbooks" / playbook),
               "--extra-vars", json.dumps(extra)]
    if args.operation in {"plan", "verify"}:
        command.append("--check")
    with (lock_root / key).open("a") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error("Another workflow holds the local APIC lock")
        environment = dict(os.environ, ANSIBLE_CONFIG=str(ROOT / "ansible.cfg"))
        result = subprocess.run(command, cwd=ROOT, env=environment, check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
