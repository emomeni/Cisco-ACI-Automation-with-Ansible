.PHONY: install test validate syntax check
install:
	python -m pip install -r requirements-dev.txt -c constraints.txt
	ansible-galaxy collection install -r collections/requirements.yml -p .ansible/collections

validate:
	python scripts/validate.py examples/full-stack.yml examples/tenant-only.yml

test:
	python -m pytest -q

syntax:
	ansible-playbook --syntax-check playbooks/site.yml
	ansible-playbook --syntax-check playbooks/verify.yml
	ansible-playbook --syntax-check playbooks/snapshot.yml

check: validate test syntax
	yamllint .
	python scripts/check_collection.py
