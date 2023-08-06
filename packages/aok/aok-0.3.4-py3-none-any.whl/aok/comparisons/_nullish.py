import typing

import yaml

from aok import _definitions


class Optional(_definitions.Comparator):
    """Compares two value as an equality or allow None."""

    def __init__(self):
        """Create an optional comparison object."""
        super(Optional, self).__init__(None)

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        """Make an optional equality comparison."""
        return observed is None or observed == self.value

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "Optional":
        return cls()


class NotNull(_definitions.Comparator):
    """Won't allow a value to be null."""

    def __init__(self):
        """Create a non-null comparison object."""
        super(NotNull, self).__init__(None)

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        """Make an optional equality comparison."""
        return observed is not None

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "NotNull":
        return cls()


NotNull.register()
not_null = getattr(NotNull, "constructor", NotNull)

Optional.register()
optional = getattr(Optional, "constructor", Optional)

__all__ = [
    "NotNull",
    "not_null",
    "Optional",
    "optional",
]
