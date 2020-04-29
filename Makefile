.PHONY: install setup lint test integration all-tests check-sec rabbitmq

install:
	@pip install -e .

setup: install
	@pip install -r requirements/requirements_test.txt

lint:
	@flake8 barterdude tests tests_integration

test:
	@nosetests -s --exclude="tests_integration" --with-coverage --cover-erase --cover-package=barterdude

integration:
	@nosetests -s -w tests_integration/

all-tests: test integration lint check-sec

all-tests-container:
	@docker-compose run --rm barterdude make all-tests

check-sec:
	@echo "Running Bandit..."
	@bandit -r .

rabbitmq:
	@docker run -d --rm --name barterdude_rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.7.24-management-alpine
