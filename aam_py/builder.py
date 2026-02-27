import os
from typing import List, Iterable, Union

class SchemaField:
    """A single field declaration inside a `@schema` block."""
    __slots__ = ('name', 'type_name', 'is_optional')

    def __init__(self, name: str, type_name: str, is_optional: bool = False):
        self.name = name
        self.type_name = type_name
        self.is_optional = is_optional

    @classmethod
    def required(cls, name: str, type_name: str) -> 'SchemaField':
        return cls(name, type_name, False)

    @classmethod
    def optional(cls, name: str, type_name: str) -> 'SchemaField':
        return cls(name, type_name, True)

    def to_aaml(self) -> str:
        if self.is_optional:
            return f"{self.name}*: {self.type_name}"
        return f"{self.name}: {self.type_name}"

class AAMBuilder:
    """Fluent builder for constructing AAML configuration content programmatically."""
    __slots__ = ('_buffer',)

    def __init__(self):
        self._buffer: List[str] = []

    def _push_sep(self) -> None:
        if self._buffer:
            self._buffer.append('\n')

    def add_line(self, key: str, value: str) -> 'AAMBuilder':
        self._push_sep()
        self._buffer.append(f"{key} = {value}")
        return self

    def comment(self, text: str) -> 'AAMBuilder':
        self._push_sep()
        self._buffer.append(f"# {text}")
        return self

    def schema(self, name: str, fields: Iterable[SchemaField]) -> 'AAMBuilder':
        self._push_sep()
        fields_str = ", ".join(f.to_aaml() for f in fields)
        self._buffer.append(f"@schema {name} {{ {fields_str} }}")
        return self

    def schema_multiline(self, name: str, fields: Iterable[SchemaField]) -> 'AAMBuilder':
        self._push_sep()
        self._buffer.append(f"@schema {name} {{")
        for field in fields:
            self._buffer.append(f"\n    {field.to_aaml()}")
        self._buffer.append("\n}")
        return self

    def derive(self, path: str, schemas: Iterable[str] = ()) -> 'AAMBuilder':
        self._push_sep()
        base = f"@derive {path}"
        schemas_list = list(schemas)
        if schemas_list:
            base += "::" + "::".join(schemas_list)
        self._buffer.append(base)
        return self

    def import_path(self, path: str) -> 'AAMBuilder':
        self._push_sep()
        self._buffer.append(f"@import {path}")
        return self

    def type_alias(self, alias: str, type_name: str) -> 'AAMBuilder':
        self._push_sep()
        self._buffer.append(f"@type {alias} = {type_name}")
        return self

    def add_raw(self, raw_line: str) -> 'AAMBuilder':
        self._push_sep()
        self._buffer.append(raw_line)
        return self

    def to_file(self, path: Union[str, os.PathLike]) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            f.write("".join(self._buffer))

    def build(self) -> str:
        return "".join(self._buffer)

    def __str__(self) -> str:
        return self.build()
