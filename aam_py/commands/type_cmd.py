from aam_py.error import ParseError, NotFoundError
from aam_py.types import resolve_builtin
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from aam_py.aaml import AAML

class TypeCommand:
    @property
    def name(self) -> str:
        return "type"

    def execute(self, aaml: 'AAML', args: str) -> None:
        parts = [p.strip() for p in args.split('=', 1)]
        if len(parts) != 2:
            raise ParseError(0, f"@type {args}", "Expected format: @type alias = type_name")
            
        alias = parts[0]
        type_name = parts[1]
        
        if not alias or not type_name:
            raise ParseError(0, f"@type {args}", "Alias and type name cannot be empty")
            
        type_def = aaml.get_type(type_name)
        if type_def is not None:
            aaml.register_type(alias, type_def)
            return
            
        try:
            builtin = resolve_builtin(type_name)
            aaml.register_type(alias, builtin)
        except NotFoundError:
            raise ParseError(0, f"@type {args}", f"Unknown type to alias: '{type_name}'")
