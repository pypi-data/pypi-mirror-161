import typing

import yaml

from aok import _definitions
from aok import _operations


class Equals(_definitions.Comparator):
    """Compares two values as an equality."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        """Make an equals comparison."""
        return _operations.cast_compatible(self.value, observed) == observed


class Unequals(_definitions.Comparator):
    """Compares two values as an inequality."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        """Make an inequality comparison."""
        return _operations.cast_compatible(self.value, observed) != observed


class Anything(_definitions.Comparator):
    """Allows anything for the given value."""

    def __init__(self):
        """Create an Anything comparison operation."""
        super(Anything, self).__init__(None)

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        """Anything will always be true."""
        return True

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "Anything":
        return cls()


class Less(_definitions.Comparator):
    """Allows anything less than the given value."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        """Less than will be true."""
        return _operations.cast_compatible(self.value, observed) > observed


class LessOrEqual(_definitions.Comparator):
    """Allows anything less than or equal the given value."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        """Less than or equal will be true."""
        return _operations.cast_compatible(self.value, observed) >= observed


class Greater(_definitions.Comparator):
    """Allows anything greater than the given value."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        """Greater than will be true."""
        return _operations.cast_compatible(self.value, observed) < observed


class GreaterOrEqual(_definitions.Comparator):
    """Allows anything greater than or equal to the given value."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        """Greater than or equal will be true."""
        return _operations.cast_compatible(self.value, observed) <= observed


class Between(_definitions.Comparator):
    """Allows between the given values."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        """Greater than or equal will be true."""
        casted_min = _operations.cast_compatible(self.value["min"], observed)
        casted_max = _operations.cast_compatible(self.value["max"], observed)
        return casted_min <= observed <= casted_max

    @classmethod
    def construct(cls, minimum: typing.Any, maximum: typing.Any) -> "Between":
        """Create a Between comparison operator with the specified options."""
        return cls({"min": minimum, "max": maximum})

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "Between":
        if isinstance(node, yaml.SequenceNode):
            loaded = loader.construct_sequence(node, deep=True)
            value = {"min": loaded[0], "max": loaded[1]}
        else:
            value = loader.construct_mapping(node, deep=True)
        return cls(value)


class OneOf(_definitions.Comparator):
    """Allows a matching comparison between any of the listed values."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        """Succeeds if at least one of the options are equal."""
        failures: typing.Dict[str, _definitions.Comparison] = {}
        for index, option in enumerate(self.value["options"]):
            if isinstance(option, _definitions.Comparator):
                comparator = option
            else:
                comparator = Equals(option)

            result = comparator.compare(observed, subset=subset)
            if getattr(result, "success", result):
                return result

            if isinstance(result, _definitions.Comparison):
                failures[str(index)] = result
            else:
                failures[str(index)] = _definitions.Comparison(
                    operation=comparator.operation_name(),
                    success=False,
                    expected=comparator.value,
                    observed=observed,
                )

        return _definitions.Comparison(
            operation="one_of",
            success=False,
            expected=", ".join([f"({i}) {f.expected}" for i, f in failures.items()]),
            observed=observed,
        )

    @classmethod
    def construct(cls, options: typing.List[typing.Any]) -> "OneOf":
        """Create a OneOf comparison operator with the specified options."""
        return cls({"options": options})

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "OneOf":
        options = loader.construct_sequence(node, deep=True)
        return cls({"options": options})


class NoneOf(_definitions.Comparator):
    """Allows a mismatching comparison between none of the listed values."""

    def _compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> typing.Union[_definitions.Comparison, bool]:
        """Succeeds if none of the options are equal."""
        for index, option in enumerate(self.value["options"]):
            if isinstance(option, _definitions.Comparator):
                comparator = option
            else:
                comparator = Equals(option)

            result = comparator.compare(observed, subset=subset)
            if getattr(result, "success", False):
                return _definitions.Comparison(
                    operation=f"not {result.operation}",
                    success=False,
                    expected=result.expected,
                    observed=result.observed,
                    children=result.children,
                )

        return _definitions.Comparison(
            operation="none_of",
            success=True,
            expected=self.value,
            observed=observed,
        )

    @classmethod
    def construct(cls, options: typing.List[typing.Any]) -> "NoneOf":
        """Create a NoneOf comparison operator with the specified options."""
        return cls({"options": options})

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "NoneOf":
        options = loader.construct_sequence(node, deep=True)
        return cls({"options": options})


Anything.register()
anything = getattr(Anything, "constructor", Anything)

Between.register()
between = getattr(Between, "constructor", Between)

Equals.register()
equals = getattr(Equals, "constructor", Equals)

Unequals.register()
unequals = getattr(Unequals, "constructor", Unequals)

Greater.register()
greater = getattr(Greater, "constructor", Greater)

GreaterOrEqual.register()
greater_or_equal = getattr(GreaterOrEqual, "constructor", GreaterOrEqual)

Less.register()
less = getattr(Less, "constructor", Less)

LessOrEqual.register()
less_or_equal = getattr(LessOrEqual, "constructor", LessOrEqual)

NoneOf.register()
none_of = getattr(NoneOf, "constructor", NoneOf)

OneOf.register()
one_of = getattr(OneOf, "constructor", OneOf)
