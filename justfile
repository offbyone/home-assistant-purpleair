# Run tests
test:
    uv run pytest -v

# Bootstrap the development environment
bootstrap: ensure-uv install-deps

# Refresh/update dependencies
refresh: compile-deps install-deps

ensure-uv:
    #!/usr/bin/env bash
    if ! command -v uv >/dev/null 2>&1; then
        echo "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi
    uv venv

compile-deps:
    uv pip compile --python-platform=linux dev-requirements.in -o dev-requirements.txt

install-deps:
    uv pip install -r dev-requirements.txt
