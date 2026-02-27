class AamlError(Exception):
    """Base exception for all AAML errors."""
    pass

class IoError(AamlError):
    """An I/O error occurred while reading a file."""
    def __init__(self, message: str):
        super().__init__(f"IO Error: {message}")

class ParseError(AamlError):
    """A line could not be parsed as a valid AAML statement."""
    __slots__ = ('line', 'content', 'details')

    def __init__(self, line: int, content: str, details: str):
        self.line = line
        self.content = content
        self.details = details
        super().__init__(f"Parse Error at line {line}: '{content}'. Reason: {details}")

class NotFoundError(AamlError):
    """A key or type name was not found in the registry or map."""
    __slots__ = ('key',)

    def __init__(self, key: str):
        self.key = key
        super().__init__(f"Key not found: '{key}'")

class InvalidValueError(AamlError):
    """A value does not satisfy a basic type constraint."""
    def __init__(self, message: str):
        super().__init__(f"Invalid value: {message}")

class InvalidTypeError(AamlError):
    """A value failed validation against a registered or built-in type."""
    __slots__ = ('type_name', 'details')

    def __init__(self, type_name: str, details: str):
        self.type_name = type_name
        self.details = details
        super().__init__(f"Invalid type '{type_name}': {details}")

class DirectiveError(AamlError):
    """A directive encountered an error in its arguments."""
    __slots__ = ('cmd', 'msg')

    def __init__(self, cmd: str, msg: str):
        self.cmd = cmd
        self.msg = msg
        super().__init__(f"Directive '@{cmd}' error: {msg}")

class SchemaValidationError(AamlError):
    """A schema constraint was violated during parsing or explicit validation."""
    __slots__ = ('schema', 'field', 'type_name', 'details')

    def __init__(self, schema: str, field: str, type_name: str, details: str):
        self.schema = schema
        self.field = field
        self.type_name = type_name
        self.details = details
        super().__init__(f"Schema '{schema}' validation error: field '{field}' (type '{type_name}') — {details}")
