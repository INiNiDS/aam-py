# aam-py

Welcome to the `aam-py` documentation. This is a Python implementation of the Abstract Alias Mapping (AAM) parser and configuration system.

## Overview

The `aam-py` library is designed to parse AAML (Abstract Alias Mapping Language) files, validate their schemas, correctly assign data types, and expose an easy-to-use querying system for those configurations.

## Installation

```bash
pip install aam-py
```

## Quick Start

```python
from aam_py.builder import AAMBuilder, SchemaField
from aam_py.types.primitive import PrimitiveType

builder = AAMBuilder()
builder.add_schema(
    SchemaField("host", PrimitiveType.String),
    SchemaField("port", PrimitiveType.Integer)
)

parser = builder.build()
aaml = parser.parse_file("config.aaml")

print(aaml.get("host").as_string())
print(aaml.get("port").as_integer())
```
