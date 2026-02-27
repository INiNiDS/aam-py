from typing import Optional, List

from aam_py.error import AamlError, InvalidValueError, NotFoundError
from aam_py.types import Type
from aam_py.types.primitive_type import PrimitiveType

def split_top_level(s: str) -> List[str]:
    items = []
    depth = 0
    cur = []
    
    for ch in s:
        if ch in ('{', '['):
            depth += 1
            cur.append(ch)
        elif ch in ('}', ']'):
            depth -= 1
            cur.append(ch)
        elif ch == ',' and depth == 0:
            t = ''.join(cur).strip()
            if t:
                items.append(t)
            cur.clear()
        else:
            cur.append(ch)
            
    t = ''.join(cur).strip()
    if t:
        items.append(t)
    return items


class ListType(Type):
    __slots__ = ('inner_type',)

    def __init__(self, inner_type: str):
        self.inner_type = inner_type

    @classmethod
    def from_name(cls, name: str) -> 'Type':
        raise NotFoundError("ListType.from_name — use ListType() instead")

    def base_type(self) -> 'Type':
        return PrimitiveType.STRING

    @staticmethod
    def parse_inner(type_str: str) -> Optional[str]:
        t = type_str.strip()
        if t.startswith("list<") and t.endswith(">"):
            inner = t[5:-1].strip()
            if inner:
                return inner
        return None

    @staticmethod
    def parse_items(value: str) -> Optional[List[str]]:
        t = value.strip()
        if t.startswith("[") and t.endswith("]"):
            inner = t[1:-1].strip()
            return split_top_level(inner)
        return None

    def validate(self, value: str) -> None:
        items = self.parse_items(value)
        if items is None:
            raise InvalidValueError(f"Expected a list literal in the form [item, item, ...], got '{value}'")
            
        from aam_py.types import resolve_builtin
        try:
            inner = resolve_builtin(self.inner_type)
        except AamlError:
            raise NotFoundError(f"Unknown list element type '{self.inner_type}'")
            
        for item in items:
            try:
                inner.validate(item)
            except AamlError as e:
                raise InvalidValueError(f"List item '{item}' failed validation for type '{self.inner_type}': {e}")
