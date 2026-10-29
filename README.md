# API Client Project

## Overview

A Python API client for the Training Mock API, demonstrating HTTP requests, retries, pagination, response validation, and automated testing.

## Features

- HTTP requests using `httpx`
- Request timeout configuration
- Retries for HTTP 429 and 5xx responses
- Exponential backoff with jitter
- Support for the `Retry-After` header
- Offset-based pagination
- Pydantic validation of parcel records
- Unit tests using `httpx.MockTransport`

## Project Structure

```text
project4/
├── apiclient/
│   ├── client.py
│   └── models.py
├── tests/
│   └── test_client.py
├── starter_kit/
│   └── mock_api/
├── test_client_demo.py
└── README.md
```

## Setup

Install the dependencies:

```bash
uv sync --project starter_kit
```

## Quality Checks

```bash
uv run --project starter_kit ruff check .
uv run --project starter_kit ruff format --check .
uv run --project starter_kit mypy apiclient
uv run --project starter_kit pytest -v
uv run --project starter_kit pre-commit run --all-files
```

## Testing

The client tests use a fake HTTP transport to test API behavior without making real network requests. Tests should cover successful requests, retries, timeout exceptions, and invalid-record validation.

## Git Workflow

Create a feature branch, run quality checks, commit your changes, push the branch, and open a pull request.