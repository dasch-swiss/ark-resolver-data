# Determine this makefile's path.
# Be sure to place this BEFORE `include` directives, if any.
# THIS_FILE := $(lastword $(MAKEFILE_LIST))
THIS_FILE := $(abspath $(lastword $(MAKEFILE_LIST)))
CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

.PHONY: install
install: ## install requirements in local env
	pip3 install -r requirements.txt

.PHONY: test
test: ## run ark-resolver-data tests inside docker image from local env
	docker-compose up -d
	@while [ "`docker-compose logs ark | grep -o "Starting worker"`" != "Starting worker" ]; do sleep 3; done;
	cd tests && py.test --disable-warnings
	docker-compose down

.PHONY: help
help: ## this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.DEFAULT_GOAL := help
