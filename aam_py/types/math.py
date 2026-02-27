from enum import Enum

from aam_py.error import AamlError, NotFoundError, InvalidValueError
from aam_py.types import Type
from aam_py.types.primitive_type import PrimitiveType

class MathTypes(Type, Enum):
    VECTOR2 = "vector2"
    VECTOR3 = "vector3"
    VECTOR4 = "vector4"
    QUATERNION = "quaternion"
    MATRIX3X3 = "matrix3x3"
    MATRIX4X4 = "matrix4x4"

    @classmethod
    def from_name(cls, name: str) -> 'Type':
        for mt in cls:
            if mt.value == name:
                return mt
        raise NotFoundError(name)

    def base_type(self) -> 'PrimitiveType':
        return PrimitiveType.F64

    def validate(self, value: str) -> None:
        parts = [p.strip() for p in value.split(',')]
        
        expected_len = 0
        if self == MathTypes.VECTOR2:
            expected_len = 2
        elif self == MathTypes.VECTOR3:
            expected_len = 3
        elif self in (MathTypes.VECTOR4, MathTypes.QUATERNION):
            expected_len = 4
        elif self == MathTypes.MATRIX3X3:
            expected_len = 9
        elif self == MathTypes.MATRIX4X4:
            expected_len = 16

        if len(parts) != expected_len:
            raise InvalidValueError(f"Expected {expected_len} components, got {len(parts)}")

        for part in parts:
            try:
                float(part)
            except ValueError:
                raise InvalidValueError(f"Invalid number: {part}")
