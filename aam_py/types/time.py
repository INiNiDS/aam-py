from enum import Enum

from aam_py.error import AamlError, NotFoundError, InvalidValueError
from aam_py.types import Type
from aam_py.types.primitive_type import PrimitiveType

def validate_date_part(date: str) -> bool:
    parts = date.split('-')
    if len(parts) != 3:
        return False
    if len(parts[0]) != 4 or len(parts[1]) != 2 or len(parts[2]) != 2:
        return False
    try:
        int(parts[0])
        int(parts[1])
        int(parts[2])
        return True
    except ValueError:
        return False

def validate_datetime(value: str) -> None:
    if len(value) < 10 or not validate_date_part(value[:10]):
        raise InvalidValueError(f"Invalid DateTime '{value}': expected ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")

def validate_numeric(value: str, label: str) -> None:
    try:
        float(value)
    except ValueError:
        raise InvalidValueError(f"Invalid {label} '{value}': expected a number")

class TimeTypes(Type, Enum):
    DATETIME = "datetime"
    DURATION = "duration"
    YEAR = "year"
    DAY = "day"
    HOUR = "hour"
    MINUTE = "minute"

    @classmethod
    def from_name(cls, name: str) -> 'Type':
        for tt in cls:
            if tt.value == name:
                return tt
        raise NotFoundError(name)

    def base_type(self) -> 'PrimitiveType':
        return PrimitiveType.F64

    def validate(self, value: str) -> None:
        if self == TimeTypes.DATETIME:
            validate_datetime(value)
        elif self == TimeTypes.DURATION:
            if value.startswith('P'):
                pass  # ISO 8601 duration
            else:
                validate_numeric(value, "Duration")
        elif self == TimeTypes.YEAR:
            validate_numeric(value, "Year")
        elif self == TimeTypes.DAY:
            validate_numeric(value, "Day")
        elif self == TimeTypes.HOUR:
            validate_numeric(value, "Hour")
        elif self == TimeTypes.MINUTE:
            validate_numeric(value, "Minute")
