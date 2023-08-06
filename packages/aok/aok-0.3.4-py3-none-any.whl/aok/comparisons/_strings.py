import fnmatch
import re
import typing

import yaml

from aok import _definitions


class Contains(_definitions.Comparator):
    """Compares strings for a subset exact match."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        return self.value in observed

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "Contains":
        value: str = loader.construct_python_str(node)
        return cls(value)


class NotContains(_definitions.Comparator):
    """Compares strings for a subset exact mismatch."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        return self.value not in observed

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "NotContains":
        value: str = loader.construct_python_str(node)
        return cls(value)


class Like(_definitions.Comparator):
    """Compares strings using unix-shell wildcard like regexes."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        return fnmatch.fnmatch(observed, self.value)

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "Like":
        value: str = loader.construct_python_str(node)
        return cls(value)


class NotLike(_definitions.Comparator):
    """Compare strings using unix-shell wildcard like regexes."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        return not fnmatch.fnmatch(observed, self.value)

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "NotLike":
        value: str = loader.construct_python_str(node)
        return cls(value)


class LikeCase(_definitions.Comparator):
    """Compares strings using unix-shell wildcard like regexes."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        return fnmatch.fnmatchcase(observed, self.value)

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "LikeCase":
        value: str = loader.construct_python_str(node)
        return cls(value)


class Match(_definitions.Comparator):
    """Compare strings using the compiled regex."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        """Determine if the value matches the regular expression."""
        pattern = re.compile(self.value["regex"], flags=self.value.get("flags", 0))
        return pattern.match(observed) is not None

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "Match":
        if isinstance(node, yaml.ScalarNode):
            regex = loader.construct_python_str(node)
            value = {"regex": regex}
        else:
            value = loader.construct_mapping(node, deep=True)
        return cls(value)


Contains.register()
contains = getattr(Contains, "constructor", Contains)

NotContains.register()
not_contains = getattr(NotContains, "constructor", NotContains)

Like.register()
like = getattr(Like, "constructor", Like)

NotLike.register()
not_like = getattr(NotLike, "constructor", NotLike)

LikeCase.register()
like_case = getattr(LikeCase, "constructor", LikeCase)

Match.register()
match = getattr(Match, "constructor", Match)

__all__ = [
    "Contains",
    "contains",
    "NotContains",
    "not_contains",
    "Like",
    "like",
    "NotLike",
    "not_like",
    "LikeCase",
    "like_case",
    "Match",
    "match",
]
