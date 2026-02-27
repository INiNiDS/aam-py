# Contributing to aam-py

Thank you for your interest in contributing to **aam-py**! 🎉

We welcome bug reports, feature requests, documentation improvements, and pull requests of all sizes.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)

---

## Code of Conduct

By participating in this project you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

---

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/aam-py.git
   cd aam-py
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/INiNiDS/aam-py.git
   ```

---

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

```bash
# Create a virtual environment and install dependencies
uv sync

# Activate the environment
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

Requires **Python ≥ 3.14**.

---

## Running Tests

```bash
pytest tests/
```

To run with coverage:

```bash
pytest --cov=aam_py tests/
```

All tests must pass before a pull request can be merged.

---

## Submitting Changes

1. Create a new branch from `main`:
   ```bash
   git checkout -b feat/my-feature
   ```
   Use a descriptive prefix: `feat/`, `fix/`, `docs/`, `refactor/`, `test/`, `chore/`.

2. Make your changes and commit using clear, imperative messages:
   ```
   feat: add support for nested schema derivation
   fix: handle empty list type gracefully
   docs: add quick-start example to README
   ```

3. Push your branch and open a **Pull Request** against `main`.

4. Fill in the pull request template completely.

5. Ensure all CI checks pass (tests, linting).

---

## Code Style

- Follow **[PEP 8](https://pep8.org/)**.
- Use type annotations for all public functions and methods.
- Keep functions focused and small.
- Add docstrings to all public classes, functions, and modules.
- Run `ruff` or `flake8` before committing.

---

## Reporting Bugs

Open an issue using the **Bug Report** template and include:

- A minimal, reproducible example
- The AAML input that triggers the issue
- Expected vs. actual behaviour
- Python version and OS

---

## Requesting Features

Open an issue using the **Feature Request** template. Describe:

- The problem you are trying to solve
- Your proposed solution
- Any alternatives you considered

---

## Questions?

Feel free to open a [Discussion](https://github.com/INiNiDS/aam-py/discussions) for questions that don't fit neatly into bug reports or feature requests.
