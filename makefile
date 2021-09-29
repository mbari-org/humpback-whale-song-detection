# Type check and test
default:
	make check test

# Install dependencies
install:
	pip install -r requirements.txt

# Do static type checking
check:
	python -m mypy hwsd --ignore-missing-imports

# Install std types for mypy
install-types:
	python -m mypy --install-types

# Run tests
test:
	python -m pytest --show-capture=all

# Format source code
format:
	python -m black hwsd
