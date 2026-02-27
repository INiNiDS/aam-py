from aam_py.error import ParseError
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from aam_py.aaml import AAML, Command

class ImportCommand:
    @property
    def name(self) -> str:
        return "import"

    def execute(self, aaml: 'AAML', args: str) -> None:
        path = aaml.unwrap_quotes(args.strip())
        if not path:
            raise ParseError(0, f"@import {args}", "Missing file path")
        aaml.merge_file(path)
