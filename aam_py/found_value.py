from collections import UserString

class FoundValue(UserString):
    """
    Lookup result wrapper.
    It can be used like a normal string, but provides helper methods
    for modification similar to the Rust FoundValue.
    """
    __slots__ = ()

    def __init__(self, seq: str):
        super().__init__(seq)

    def remove(self, sub: str) -> None:
        """Removes all occurrences of `sub` from the string in-place."""
        self.data = self.data.replace(sub, "")

    def as_str(self) -> str:
        """Returns the underlying string."""
        return self.data

    def __repr__(self) -> str:
        return repr(self.data)
