.PHONY: venv smoke test tree

venv:
bash scripts/bootstrap_venv.sh

smoke:
bash scripts/run_smoke.sh

test:
. .venv/bin/activate && PYTHONPATH=src pytest -q

tree:
find . -maxdepth 4 -type f | sort
