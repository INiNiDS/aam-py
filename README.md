# aam-py

> A Python implementation of the **Abstract Alias Mapping Language (AAML)** parser and configuration system.

[![PyPI version](https://img.shields.io/pypi/v/aam-py.svg)](https://pypi.org/project/aam-py/)
[![Python](https://img.shields.io/pypi/pyversions/aam-py.svg)](https://pypi.org/project/aam-py/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/INiNiDS/aam-py/actions/workflows/tests.yml/badge.svg)](https://github.com/INiNiDS/aam-py/actions)
[![Read the Docs](https://img.shields.io/readthedocs/aam-py)](https://aam-py.readthedocs.io)

---

## Overview

**aam-py** is a Python port of the [`aam-rs`](https://github.com/INiNiDS/aam-rs) Rust library. It provides a full-featured AAML parser, validator, and serializer for defining and consuming structured configuration schemas.

AAML (Abstract Alias Mapping Language) is a configuration language built around:
- **Schemas** — typed field definitions with validation rules
- **Aliases** — short names that map to complex type structures
- **Derivation** — composition of schemas from other schemas

---

## Features

- 🔍 **Parser** — parse `.aaml` configuration files into Python objects
- ✅ **Validator** — validate config values against defined schemas
- 📦 **Serializer** — serialize parsed structures back to AAML or JSON-compatible dicts
- 🧩 **Type system** — rich built-in type registry (primitives, math types, time types, lists)
- 🐍 **Pure Python** — no compiled extensions required

---

## Installation

Requires **Python ≥ 3.14**.

```bash
pip install aam-py
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add aam-py
```

---

## Quick Start

```python
from aam_py import AAML

aaml = AAML()

schema_src = """
schema Point {
    x: float
    y: float
}
"""

aaml.load(schema_src)

value = aaml.get("Point.x")
print(value)
```

---

## Documentation

Full API reference and guides are available at **[aam-py.readthedocs.io](https://aam-py.readthedocs.io)**.

---

## Contributing

Contributions are welcome! Please read the [Contributing Guide](CONTRIBUTING.md) before submitting a pull request.

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold its standards.

---

## Security

If you discover a security vulnerability, please follow the process described in [SECURITY.md](SECURITY.md).

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.
