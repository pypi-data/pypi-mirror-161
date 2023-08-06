import json
import textwrap
import typing

import yaml
import yaml.constructor

import aok
from aok import _definitions
from aok import _types


def _compare_dicts(
    expected: "_types.ArbitraryDict",
    observed: typing.Any,
    subset: bool,
) -> "_definitions.Comparison":
    """Compare dictionaries recursively and returns the results as a Comparison."""
    expected_value = expected or {}
    observed_value = observed or {}

    if not isinstance(observed_value, dict):
        return _definitions.Comparison(
            operation="dict_type",
            success=False,
            expected=str(type(expected_value)),
            observed=str(type(observed_value)),
        )

    keys = set(list(expected_value.keys()))
    if not subset:
        keys.update(set(list(observed_value.keys())))

    results: typing.Dict[typing.Any, _definitions.Comparison] = {
        key: (
            aok.to_comparator(expected_value.get(key)).compare(
                observed_value.get(key), subset
            )
        )
        for key in keys
    }

    return _definitions.Comparison(
        operation="dict_comparison",
        success=all([r.success for r in results.values()]),
        expected=expected_value,
        observed=observed,
        children=results,
    )


class Dict(_definitions.Comparator):
    """Main class in which aok assertions are made."""

    def compare(
        self,
        observed: "_types.ArbitraryDict",
        subset: bool = False,
    ) -> _definitions.Comparison:
        """Compare the observed dictionary in a recursive fashion."""
        return _compare_dicts(
            expected=typing.cast(_types.ArbitraryDict, self.value or {}),
            observed=observed,
            subset=subset,
        )


class JsonDict(_definitions.Comparator):
    """Dictionary comparator for data stored as a JSON string."""

    def compare(
        self,
        observed: str,
        subset: bool = False,
    ) -> _definitions.Comparison:
        """Parse and compare the observed value."""
        try:
            observed_parsed = json.loads(observed or "{}")
            if not isinstance(observed_parsed, dict):
                raise ValueError("Not a JSON-serialized dictionary.")
        except Exception as error:
            return _definitions.Comparison(
                operation="json_dict",
                success=False,
                expected=self.value,
                observed=observed,
                error=error,
            )

        return _compare_dicts(
            expected=typing.cast(_types.ArbitraryDict, self.value or {}),
            observed=observed_parsed,
            subset=subset,
        )

    @classmethod
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "JsonDict":
        """Load the dict from a yaml parser."""
        try:
            return cls(value=loader.construct_mapping(node, deep=True))
        except yaml.constructor.ConstructorError:
            if node.value == "":
                return cls(value={})
            raise


class Okay(Dict):
    """Root dictionary object for comparison."""

    def assert_subset(
        self,
        observed: "_types.ArbitraryDict",
        message: str = None,
    ) -> None:
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

    def assert_all(
        self,
        observed: "_types.ArbitraryDict",
        message: str = None,
    ) -> None:
        """
        Compare the observed object against the expected values.

        This is carried out in a recursive, element-wise fashion and raises assertion
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
    def _from_yaml(cls, loader: yaml.Loader, node: yaml.Node) -> "Okay":
        """Load the dict from a yaml parser."""
        try:
            return cls(value=loader.construct_mapping(node, deep=True))
        except yaml.constructor.ConstructorError:
            if node.value == "":
                return cls(value={})
            raise

    @classmethod
    def register(cls):
        """Override the registration in this case for base registration."""
        yaml.add_constructor("!aok", Okay.parse_yaml)


Okay.register()

JsonDict.register()
