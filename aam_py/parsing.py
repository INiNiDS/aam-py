from typing import Optional, Tuple, List, Dict

def strip_comment(line: str) -> str:
    """Strips an inline `#` comment from a raw source line, respecting quoted strings."""
    quote_state = None
    
    for idx, c in enumerate(line):
        if quote_state is None and c == '#':
            preceded_by_space = idx == 0 or line[idx - 1].isspace()
            followed_by_space = idx + 1 == len(line) or line[idx + 1].isspace()
            if preceded_by_space and followed_by_space:
                return line[:idx]
                
        elif quote_state is None and c in ('"', "'"):
            quote_state = c
        elif quote_state == c:
            quote_state = None
            
    return line

def unwrap_quotes(s: str) -> str:
    """Strips a matching pair of surrounding `"…"` or `'…'` quotes from `s`."""
    s = s.strip()
    if len(s) >= 2:
        if s.startswith('"') and s.endswith('"'):
            return s[1:-1]
        if s.startswith("'") and s.endswith("'"):
            return s[1:-1]
    return s

def parse_assignment(line: str) -> Tuple[str, str]:
    """
    Parses a `key = value` assignment and returns trimmed (key, value).
    Raises ValueError with error message string on failure.
    """
    depth = 0
    eq_pos = -1
    
    for i, ch in enumerate(line):
        if ch in ('{', '['):
            depth += 1
        elif ch in ('}', ']'):
            depth -= 1
        elif ch == '=' and depth == 0:
            eq_pos = i
            break
            
    if eq_pos == -1:
        raise ValueError("Missing assignment operator '='")
        
    key = line[:eq_pos].strip()
    raw_val = line[eq_pos + 1:].strip()
    
    if not key:
        raise ValueError("Key cannot be empty")
        
    if raw_val.startswith('{') or raw_val.startswith('['):
        val = raw_val
    else:
        val = unwrap_quotes(raw_val)
        
    return key, val

def needs_accumulation(text: str) -> bool:
    """Returns True if text is a directive opening a block not yet closed."""
    if not text.startswith('@'):
        return False
    opens = text.count('{')
    closes = text.count('}')
    return opens > closes

def block_is_complete(buf: str) -> bool:
    """Returns True if the buffer has at least as many `}` as `{`."""
    opens = buf.count('{')
    closes = buf.count('}')
    return closes >= opens

def is_inline_object(value: str) -> bool:
    """Returns True if value is an inline object literal { ... }."""
    v = value.strip()
    return v.startswith('{') and v.endswith('}')

def split_top_level_fields(s: str) -> List[str]:
    """Splits `s` on commas that are not inside `{}` or `[]`."""
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
            items.append(''.join(cur))
            cur.clear()
        else:
            cur.append(ch)
            
    items.append(''.join(cur))
    return items

def split_field_pair(entry: str) -> Tuple[str, str]:
    """Splits 'key = val' or 'key: val' on the first = or : at depth 0."""
    depth = 0
    for i, ch in enumerate(entry):
        if ch in ('{', '['):
            depth += 1
        elif ch in ('}', ']'):
            depth -= 1
        elif ch in ('=', ':') and depth == 0:
            return entry[:i], entry[i + 1:]
            
    raise ValueError(f"Inline object field '{entry}' has no '=' or ':' separator")

def parse_inline_object(value: str) -> List[Tuple[str, str]]:
    """
    Parses an inline object { key = val, ... } into key-value pairs.
    Returns structurally equivalent pairs of (key, string).
    """
    s = value.strip()
    if not s.startswith('{') or not s.endswith('}'):
        raise ValueError(f"Inline object must be wrapped in '{{}}', got: '{value}'")
        
    inner = s[1:-1]
    fields = []
    
    for entry in split_top_level_fields(inner):
        entry_trimmed = entry.strip()
        if not entry_trimmed:
            continue
            
        k, v = split_field_pair(entry_trimmed)
        k = k.strip()
        v_trimmed = v.strip()
        
        if v_trimmed.startswith('{') or v_trimmed.startswith('['):
            v_val = v_trimmed
        else:
            v_val = unwrap_quotes(v_trimmed)
            
        if not k:
            raise ValueError(f"Empty key in inline object field '{entry_trimmed}'")
            
        fields.append((k, v_val))
        
    return fields
