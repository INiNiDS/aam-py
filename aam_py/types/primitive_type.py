from enum import Enum
from typing import ClassVar

from aam_py.error import AamlError, NotFoundError, InvalidValueError
from aam_py.types import Type

class PrimitiveType(Type, Enum):
    I32 = "i32"
    F64 = "f64"
    STRING = "string"
    BOOL = "bool"
    COLOR = "color"

    @classmethod
    def from_name(cls, name: str) -> 'Type':
        for pt in cls:
            if pt.value == name:
                return pt
        raise NotFoundError(name)

    def base_type(self) -> 'PrimitiveType':
        return self

    def validate(self, value: str) -> None:
        if self == PrimitiveType.I32:
            try:
                int(value)
            except ValueError:
                raise InvalidValueError(f"Expected i32, got '{value}'")
        elif self == PrimitiveType.F64:
            try:
                float(value)
            except ValueError:
                raise InvalidValueError(f"Expected f64, got '{value}'")
        elif self == PrimitiveType.STRING:
            pass  # Any string is valid
        elif self == PrimitiveType.BOOL:
            lowered = value.lower()
            if lowered not in ("true", "false", "1", "0"):
                raise InvalidValueError(f"Expected bool (true/false/1/0), got '{value}'")
        elif self == PrimitiveType.COLOR:
            if not value.startswith('#') or len(value) not in (7, 9):
                raise InvalidValueError(f"Expected color in #RRGGBB or #RRGGBBAA format, got '{value}'")
            try:
                int(value[1:], 16)
            except ValueError:
                raise InvalidValueError(f"Invalid hex color '{value}'")
