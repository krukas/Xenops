PIP := env/bin/pip
PY := env/bin/python
FLAKE8 := env/bin/flake8
PYDOCSTYLE := env/bin/pydocstyle
COVERAGE := env/bin/coverage


help:
	@echo "COMMANDS:"
	@echo "  clean          Remove all generated files."
	@echo "  setup          Setup development environment."
	@echo "  lint           Run linters."
	@echo "  test           Run tests."
	@echo ""



clean:
	rm -rf env
	rm -rf build
	rm -rf dist
	rm -rf *.egg
	rm -rf *.egg-info
	find | grep -i ".*\.pyc$$" | xargs -r -L1 rm



virtualenv: clean
	virtualenv -p python3 env



setup: virtualenv
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt



lint:
	-$(FLAKE8) xenops
	-$(PYDOCSTYLE) xenops
	-$(FLAKE8) tests



test: lint
	$(COVERAGE) run tests/run_tests.py
