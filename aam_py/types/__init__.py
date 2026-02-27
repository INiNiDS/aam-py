from typing import Optional

from aam_py.error import AamlError, NotFoundError

class Type:
    """Core class that every AAML type must implement."""
    
    @classmethod
    def from_name(cls, name: str) -> 'Type':
        """Constructs the type from a name string."""
        raise NotImplementedError

    def base_type(self) -> 'Type':
        """Returns the primitive type that best represents this type."""
        raise NotImplementedError

    def validate(self, value: str) -> None:
        """Validates `value` against this type's constraints.
        Raises AamlError on failure.
        """
        raise NotImplementedError

def resolve_builtin(path: str) -> Type:
    """Resolves a type from a module-qualified path or a plain primitive name."""
    
    # Import locally to avoid circular dependencies
    from aam_py.types.list import ListType
    from aam_py.types.math import MathTypes
    from aam_py.types.time import TimeTypes
    from aam_py.types.physics import PhysicsTypes
    from aam_py.types.primitive_type import PrimitiveType
    
    inner = ListType.parse_inner(path)
    if inner is not None:
        return ListType(inner)
    
    parts = path.split("::", 1)
    
    try:
        if len(parts) == 2:
            module, name = parts
            if module == "math":
                return MathTypes.from_name(name)
            elif module == "time":
                return TimeTypes.from_name(name)
            elif module == "physics":
                return PhysicsTypes.from_name(name)
            else:
                raise NotFoundError(path)
        else:
            return PrimitiveType.from_name(parts[0])
    except AamlError:
        raise NotFoundError(path)
