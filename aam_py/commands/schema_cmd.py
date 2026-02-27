from aam_py.error import ParseError
from aam_py.aaml import SchemaDef
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from aam_py.aaml import AAML

class SchemaCommand:
    @property
    def name(self) -> str:
        return "schema"

    def execute(self, aaml: 'AAML', args: str) -> None:
        parts = args.split('{', 1)
        if len(parts) != 2 or '}' not in parts[1]:
            raise ParseError(0, f"@schema {args}", "Expected block enclosed in {...}")
            
        name = parts[0].strip()
        body = parts[1].rsplit('}', 1)[0].strip()
        
        if not name:
            raise ParseError(0, f"@schema {args}", "Schema name cannot be empty")
            
        fields = {}
        optional_fields = []
        
        if body:
            from aam_py.parsing import split_top_level_fields, split_field_pair
            items = split_top_level_fields(body)
            for item in items:
                item = item.strip()
                if not item:
                    continue
                try:
                    k, v = split_field_pair(item)
                except ValueError:
                    raise ParseError(0, item, "Invalid schema field (missing ':' or '=')")
                    
                k = k.strip()
                type_name = v.strip()
                
                if k.endswith('*'):
                    field_name = k[:-1].strip()
                    optional_fields.append(field_name)
                else:
                    field_name = k
                    
                if not field_name:
                    raise ParseError(0, item, "Empty field name")
                    
                fields[field_name] = type_name
                
        aaml._schemas[name] = SchemaDef(fields, optional_fields)
