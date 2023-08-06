import json
import textwrap
import typing

import yaml
import yaml.constructor

import aok
from aok import _definitions
from aok import _types


def _compare_list(
    expected: "_types.ArbitraryList",
    observed: typing.Any,
    subset: bool,
    allowed_types: typing.Tuple[typing.Any, ...] = (list, tuple),
) -> "_definitions.Comparison":
    """Compare lists recursively and returns the results as a Comparison."""
    expected_value = expected or []
    observed_value = observed or []

    if not isinstance(observed_value, allowed_types):
        return _definitions.Comparison(
            operation="list_type",
            success=False,
            expected=str(type(expected_value)),
            observed=str(type(observed_value)),
        )

    if len(expected_value) != len(observed_value):
        return _definitions.Comparison(
            operation="list_length",
            success=False,
            expected=len(expected_value),
            observed=len(observed_value),
        )

    results: typing.List[_definitions.Comparison] = [
        aok.to_comparator(exp).compare(obs, subset)
        for exp, obs in zip(expected_value, observed_value)
    ]

    return _definitions.Comparison(
        operation="list_comparison",
        success=all([r.success for r in results]),
        expected=expected_value,
        observed=observed,
        children={f"index_{i}": r for i, r in enumerate(results)},
    )


class List(_definitions.Comparator):
    """Container class for list comparisons, which compare the lists element-wise."""

    def compare(
        self,
        observed: typing.Union[typing.List[typing.Any], typing.Tuple[typing.Any, ...]],
        subset: bool = False,
    ) -> _definitions.Comparison:
        """Compare the observed list in a recursive, element-wise fashion."""
        return _compare_list(
            expected=typing.cast(_types.ArbitraryList, self.value),
            observed=observed,
            subset=subset,
        )


class StrictList(_definitions.Comparator):
    """
    Container class for list comparisons, which compare the lists element-wise.

    This only allows the specified list type and will fail if compared against a
    tuple.
    """

    def compare(
        self,
        observed: typing.Union[typing.List[typing.Any], typing.Tuple[typing.Any, ...]],
        subset: bool = False,
    ) -> _definitions.Comparison:
        """Compare the observed list in a recursive, element-wise fashion."""
        return _compare_list(
            expected=typing.cast(_types.ArbitraryList, self.value),
            observed=observed,
            subset=subset,
            allowed_types=(list,),
        )


class JsonList(_definitions.Comparator):
    """List comparator for data stored as a JSON string."""

    def compare(
        self,
        observed: str,
        subset: bool = False,
    ) -> _definitions.Comparison:
        """Parse and compare the observed value."""
        try:
            observed_parsed = json.loads(observed or "{}")
            if not isinstance(observed_parsed, list):
                raise ValueError("Not a JSON-serialized list.")
        except Exception as error:
            return _definitions.Comparison(
                operation="json_dict",
                success=False,
                expected=self.value,
                observed=observed,
                error=error,
            )

        return _compare_list(
            expected=typing.cast(_types.ArbitraryList, self.value),
            observed=observed_parsed,
            subset=subset,
        )

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "JsonList":
        """Load the list from a yaml parser."""
        try:
            return cls(value=loader.construct_sequence(node, deep=True))
        except yaml.constructor.ConstructorError:
            if node.value == "":
                return cls(value={})
            raise


class Tuple(_definitions.Comparator):
    """Container class for tuple comparisons, which compare the tuples element-wise."""

    def compare(
        self,
        observed: typing.Tuple[typing.Any, ...],
        subset: bool = False,
    ) -> _definitions.Comparison:
        """
        Compare the observed tuple against the definition.

        The comparison is carried out in a recursive, element-wise fashion.
        """
        value = typing.cast(typing.Tuple[typing.Any, ...], self.value or tuple())
        other = observed or tuple()

        if len(value) != len(other):
            return _definitions.Comparison(
                operation="tuple_length",
                success=False,
                expected=len(value),
                observed=len(other),
            )

        results: typing.List[_definitions.Comparison] = [
            aok.to_comparator(exp).compare(obs, subset)
            for exp, obs in zip(value, other)
        ]

        return _definitions.Comparison(
            operation=self.operation_name(),
            success=all([r.success for r in results]),
            expected=self.value,
            observed=observed,
            children={f"index_{i}": r for i, r in enumerate(results)},
        )


class OkayList(List):
    """Root list object for comparison."""

    def assert_subset(self, observed: "_types.ArbitraryList", message: str = None):
        """
        Compare the observed object against the expected values.

        This is carried out in a recursive, element-wise fashion and raises assertion
        errors for any deviation between the elements of the expected configuration and
        the observed structure values.

        In this subset mode, any extra keys/values found in dictionaries will be
        ignored and assumed to be insignificant. Use `assert_all` for exact matching.

        :param observed:
            Data structure to compare against the expected one.
        :param message:
            Optional assertion message to include when differences are found between
            the observed and expected data structures.
        """
        result = self.compare(observed, subset=True)
        heading = message or "One or more subset differences were found"
        assert result.success, "{}\n{}".format(
            heading,
            textwrap.indent(result.to_diff_info() or "", "  "),
        )

    def assert_all(self, observed: "_types.ArbitraryList", message: str = None):
        """
        Compare the observed object against the expected values.

        This is conducted in a recursive, element-wise fashion and raises assertion
        errors for any deviation between the elements of the expected configuration and
        the observed structure values.

        :param observed:
            Data structure to compare against the expected one.
        :param message:
            Optional assertion message to include when differences are found between
            the observed and expected data structures.
        """
        result = self.compare(observed, subset=False)
        heading = message or "One or more exact differences were found"
        assert result.success, "{}\n{}".format(
            heading,
            textwrap.indent(result.to_diff_info() or "", "  "),
        )

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "OkayList":
        """Load the list from a yaml parser."""
        try:
            return cls(value=loader.construct_sequence(node, deep=True))
        except yaml.constructor.ConstructorError:
            if node.value == "":
                return cls(value={})
            raise

    @classmethod
    def register(cls):
        """Override the registration in this case for base registration."""
        yaml.add_constructor("!aok_list", cls.parse_yaml)


OkayList.register()
List.register()
StrictList.register()
Tuple.register()

JsonList.register()
json_list = getattr(JsonList, "constructor", JsonList)
