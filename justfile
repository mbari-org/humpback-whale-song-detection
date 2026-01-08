#
# Justfile that facilitates various development tasks.
# Run them with `just` - https://github.com/casey/just.
#

# List recipes
_list:
    @just --list --unsorted

# Install uv package manager
install-uv:
    curl -LsSf https://astral.sh/uv/install.sh | sh

# Create uv environment and install dependencies
setup:
    uv sync

# Legacy setup using venv (deprecated)
setup-venv:
    #!/usr/bin/env bash
    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install -r requirements.txt

# A convenient recipe for development
dev: format check test

# Do static type checking with ty
check:
    uv run ty check hwsd

# Run tests
test:
    uv run pytest --show-capture=all

# Format source code
format:
    uv run ufmt format hwsd

# Run pylint
pylint:
    uv run pylint hwsd

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
    rm -rf .venv
