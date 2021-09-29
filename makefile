# A convenient default for development: type check, test, and format
default:
	make check test format

# As default plus pylint; good to run before committing
all:
	make check test format pylint

# Install dependencies
setup:
	pip install -r requirements.txt

# Do static type checking (not very strict)
check:
	python -m mypy hwsd

# Install std types for mypy
install-types:
	python -m mypy --install-types

# Run tests
test:
	python -m pytest --show-capture=all

# Format source code
format:
	python -m ufmt format hwsd

# Run pylint
pylint:
	python -m pylint hwsd

# Show latest few tags
tags:
	git tag -l | sort -V | tail
