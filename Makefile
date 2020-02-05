.PHONY: install setup test check-sec

install:
	@pip install -e .

setup: install
	@pip install -r requirements_test.txt

test:
	@nosetests --with-coverage --cover-erase --cover-package=barterdude
	@flake8 barterdude tests

check-sec:
	@echo "Running Bandit..."
	@bandit -r .