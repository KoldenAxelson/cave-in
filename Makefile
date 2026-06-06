# Cave In — common commands.
# Run `make` (or `make help`) to see everything available.
#
# Most targets use the project's virtualenv automatically if it exists
# (venv/bin/python), otherwise they fall back to your system python3.
# Pass extra arguments with ARGS, e.g.:  make train ARGS="--episodes 2000"

.DEFAULT_GOAL := help

PYTHON ?= python3
# Prefer the project venv if present; otherwise use PYTHON.
PY := $(shell [ -x venv/bin/python ] && echo venv/bin/python || echo $(PYTHON))
ARGS ?=

.PHONY: help setup install install-ml run play test train evaluate benchmark clean clean-brain

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-13s\033[0m %s\n", $$1, $$2}'

setup: ## Create a venv and install all dependencies (game + ML + tests)
	$(PYTHON) -m venv venv
	venv/bin/python -m pip install --upgrade pip
	venv/bin/python -m pip install pygame pytest -r requirements-ml.txt
	@echo "Setup complete. Activate with: source venv/bin/activate"

install: ## Install just the base game dependency (pygame)
	$(PY) -m pip install pygame

install-ml: ## Install ML dependencies (numpy + PyTorch) for training/Neural Net
	$(PY) -m pip install -r requirements-ml.txt

run: ## Launch the game
	$(PY) main.py

play: run ## Alias for 'run'

test: ## Run the test suite
	$(PY) -m pytest

train: ## Train the neural agent (e.g. make train ARGS="--episodes 2000")
	$(PY) tools/train_dqn.py $(ARGS)

evaluate: ## Neural agent vs path finder (e.g. make evaluate ARGS="--seeds 50")
	$(PY) tools/evaluate_agents.py $(ARGS)

benchmark: ## Benchmark path finder step count (e.g. make benchmark ARGS="--sweep 1,5,10")
	$(PY) tools/benchmark_pathfinder.py $(ARGS)

clean: ## Remove Python caches and test artifacts
	find . -type d -name __pycache__ -not -path './venv/*' -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache

clean-brain: ## Delete trained models (the saved brains)
	rm -rf models
