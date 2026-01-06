#
# Justfile that facilitates various development tasks.
# Run them with `just` - https://github.com/casey/just.
#

# List recipes
_list:
    @just --list --unsorted

# Create virtenv and install dependencies
setup:
    #!/usr/bin/env bash
    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install -r requirements.txt

# setup when python3-venv package is not available
setup_no_python3-venv:
    #!/usr/bin/env bash
    python3 -m venv venv --without-pip
    source venv/bin/activate
    curl https://bootstrap.pypa.io/get-pip.py | python
    python3 -m pip install -r requirements.txt

# A convenient recipe for development
dev: format check test

# Do static type checking (not very strict)
check:
    #!/usr/bin/env bash
    source venv/bin/activate
    python3 -m mypy hwsd

# Install std types for mypy
install-types:
    #!/usr/bin/env bash
    source venv/bin/activate
    python3 -m mypy --install-types

# Run tests
test:
    #!/usr/bin/env bash
    source venv/bin/activate
    python3 -m pytest --show-capture=all

# Format source code
format:
    #!/usr/bin/env bash
    source venv/bin/activate
    python3 -m ufmt format hwsd

# Run pylint
pylint:
    #!/usr/bin/env bash
    source venv/bin/activate
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
