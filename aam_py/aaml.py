import os
from typing import Dict, Optional, List, Tuple
from abc import ABC, abstractmethod

from aam_py.error import AamlError, NotFoundError, InvalidTypeError, ParseError
from aam_py.types import Type, resolve_builtin
from aam_py.found_value import FoundValue
from aam_py.parsing import (
    strip_comment,
    parse_assignment,
    needs_accumulation,
    block_is_complete,
    unwrap_quotes,
    is_inline_object,
    parse_inline_object
)

class SchemaDef:
    """Represents a schema definition structure."""
    __slots__ = ('fields', 'optional_fields')
    
    def __init__(self, fields: Dict[str, str], optional_fields: List[str]):
        self.fields = fields
        self.optional_fields = set(optional_fields)
        
    def is_optional(self, field: str) -> bool:
        return field in self.optional_fields

class Command(ABC):
    """Trait implemented by every AAML directive handler."""
    @property
    @abstractmethod
    def name(self) -> str:
        """The directive name without the leading `@`."""
        pass

    @abstractmethod
    def execute(self, aaml: 'AAML', args: str) -> None:
        """Executes the directive with the given argument string."""
        pass


class AAML:
    """
    The main AAML parser and configuration store.
    """
    __slots__ = ('_map', '_commands', '_types', '_schemas')

    def __init__(self):
        self._map: Dict[str, str] = {}
        self._commands: Dict[str, Command] = {}
        self._types: Dict[str, Type] = {}
        self._schemas: Dict[str, SchemaDef] = {}
        self._register_default_commands()

    # Accessors used by commands
    def get_schemas(self) -> Dict[str, SchemaDef]:
        return self._schemas
        
    def get_schema(self, name: str) -> Optional[SchemaDef]:
        return self._schemas.get(name)

    def get_map(self) -> Dict[str, str]:
        return self._map

    # Type registry
    def register_command(self, command: Command) -> None:
        self._commands[command.name] = command

    def register_type(self, name: str, type_def: Type) -> None:
        self._types[name] = type_def

    def get_type(self, name: str) -> Optional[Type]:
        return self._types.get(name)

    def unregister_type(self, name: str) -> None:
        self._types.pop(name, None)

    def check_type(self, type_name: str, value: str) -> None:
        type_def = self._types.get(type_name)
        if type_def is None:
            raise NotFoundError(type_name)
        type_def.validate(value)

    def validate_value(self, type_name: str, value: str) -> None:
        try:
            type_def = self._types.get(type_name)
            if type_def is not None:
                type_def.validate(value)
                return

            builtin = resolve_builtin(type_name)
            builtin.validate(value)
        except AamlError as e:
            raise InvalidTypeError(type_name, str(e))

    # Parsing
    def merge_content(self, content: str) -> None:
        pending: Optional[Tuple[List[str], int]] = None

        for i, line in enumerate(content.splitlines()):
            line_num = i + 1
            result = self._accumulate_or_process(line, line_num, pending)
            if isinstance(result, tuple) and isinstance(result[0], str):
                complete, start_line = result
                self._process_line(complete, start_line)
                pending = None
            elif result is not None:
                # result is a list tuple or None
                pending = result

        if pending is not None:
            buf, start = pending
            self._process_line(' '.join(buf), start)

    def _accumulate_or_process(self, line: str, line_num: int, pending: Optional[Tuple[List[str], int]]) -> Optional[Tuple]:
        if pending is not None:
            buf, start = pending
            buf.append(strip_comment(line).strip())
            joined = ' '.join(buf)
            if block_is_complete(joined):
                return (joined, start)
            return pending

        stripped = strip_comment(line).strip()
        if needs_accumulation(stripped):
            return ([stripped], line_num)

        self._process_line(line, line_num)
        return pending

    def merge_file(self, file_path: str) -> None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.merge_content(content)
        except IOError as e:
            from aam_py.error import IoError as AamlIoError
            raise AamlIoError(str(e))

    @classmethod
    def parse(cls, content: str) -> 'AAML':
        instance = cls()
        instance.merge_content(content)
        return instance

    @classmethod
    def load(cls, file_path: str) -> 'AAML':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return cls.parse(content)
        except IOError as e:
            from aam_py.error import IoError as AamlIoError
            raise AamlIoError(str(e))

    @staticmethod
    def unwrap_quotes(s: str) -> str:
        return unwrap_quotes(s)

    def _register_default_commands(self) -> None:
        from aam_py.commands.import_cmd import ImportCommand
        from aam_py.commands.type_cmd import TypeCommand
        from aam_py.commands.schema_cmd import SchemaCommand
        from aam_py.commands.derive import DeriveCommand

        self.register_command(ImportCommand())
        self.register_command(TypeCommand())
        self.register_command(SchemaCommand())
        self.register_command(DeriveCommand())

    def _process_line(self, raw_line: str, line_num: int) -> None:
        line = strip_comment(raw_line).strip()
        if not line:
            return
        if line.startswith('@'):
            self._process_directive(line[1:], line_num)
            return
        self._process_assignment(line, line_num)

    def _process_assignment(self, line: str, line_num: int) -> None:
        try:
            key, value = parse_assignment(line)
            from aam_py.validation import validate_against_schemas
            validate_against_schemas(self, key, value)
            self._map[key] = value
        except Exception as e:
            if isinstance(e, AamlError):
                raise
            raise ParseError(line_num, line, str(e))

    def _process_directive(self, content: str, line_num: int) -> None:
        parts = content.split(None, 1)
        command_name = parts[0].strip() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        if not command_name:
            raise ParseError(line_num, content, "Empty directive")

        cmd = self._commands.get(command_name)
        if cmd is not None:
            cmd.execute(self, args)
        else:
            raise ParseError(line_num, content, f"Unknown directive: @{command_name}")

    def __add__(self, other: 'AAML') -> 'AAML':
        res = AAML()
        res._map.update(self._map)
        res._commands.update(self._commands)
        res._types.update(self._types)
        res._schemas.update(self._schemas)

        res._map.update(other._map)
        res._types.update(other._types)
        return res

    def __iadd__(self, other: 'AAML') -> 'AAML':
        self._map.update(other._map)
        self._types.update(other._types)
        return self

    # Lookup Methods
    def find_obj(self, key: str) -> Optional[FoundValue]:
        if key in self._map:
            return FoundValue(self._map[key])
        return self.find_key(key)

    def find_key(self, value: str) -> Optional[FoundValue]:
        for k, v in self._map.items():
            if v == value:
                return FoundValue(k)
        return None

    def find_deep(self, key: str) -> Optional[FoundValue]:
        current_key = key
        last_found = None
        visited = set()

        while current_key in self._map:
            if current_key in visited:
                break
            visited.add(current_key)
            next_val = self._map[current_key]
            
            if next_val in visited:
                if last_found is None:
                    last_found = next_val
                break
                
            last_found = next_val
            current_key = next_val

        return FoundValue(last_found) if last_found is not None else None
