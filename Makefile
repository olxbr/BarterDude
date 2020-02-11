.PHONY: install setup lint test integration all-tests check-sec rabbitmq

install:
	@pip install -e .

setup: install
	@pip install -r requirements/requirements_test.txt

lint:
	@flake8 barterdude tests tests_integration

test:
	@nosetests --exclude="tests_integration" --with-coverage --cover-erase --cover-package=barterdude

integration:
	@nosetests -w tests_integration/

all-tests: test integration lint check-sec

check-sec:
	@echo "Running Bandit..."
	@bandit -r .

rabbitmq:
	@docker run --rm --name barterdude_rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.7.7-management-alpine