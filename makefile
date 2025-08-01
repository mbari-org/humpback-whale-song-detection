#
# Makefile that facilitates various development tasks.
#
# It is soft-linked as `justfile` in case you want to
# use `just` - https://github.com/casey/just.
#

# A convenient default for development: type check, test, and format
default: check test format

# As default plus pylint; good to run before committing
all: default pylint

# List recipes (needs `just`)
list:
	@just --list --unsorted
 
# Install dependencies
setup:
	python3 -m pip install -r requirements.txt

# Do static type checking (not very strict)
check:
	python3 -m mypy hwsd

# Install std types for mypy
install-types:
	python3 -m mypy --install-types

# Run tests
test:
	python3 -m pytest --show-capture=all

# Format source code
format:
	python3 -m ufmt format hwsd

# Run pylint
pylint:
	python3 -m pylint hwsd

# Show latest few tags
tags:
	git tag -l | sort -V | tail

clean:
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf hwsd.egg-info
	rm -rf dist
	rm -rf build
	rm -rf .ruff_cache
