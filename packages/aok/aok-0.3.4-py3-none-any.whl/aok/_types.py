import typing

from aok import _definitions

ArbitraryDict = typing.Dict[typing.Any, typing.Any]
ArbitraryList = typing.Union[typing.List[typing.Any], typing.Tuple[typing.Any, ...]]


class OkayRoot(typing.Protocol):  # pragma: no cover
    """Structural-duck-type for root Okay objects."""

    def assert_subset(
        self,
        observed: typing.Union[ArbitraryDict, ArbitraryList],
        message: str = None,
    ):
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
        pass

    def assert_all(
        self,
        observed: typing.Union[ArbitraryDict, ArbitraryList],
        message: str = None,
    ):
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
        pass

    def compare(
        self,
        observed: typing.Any,
        subset: bool = False,
    ) -> "_definitions.Comparison":
        """
        Compare the observed object against the expected values.

        This is carried out in a recursive, element-wise fashion and returns a
        comparison object that expresses the results of the compare operation.

        :param observed:
            Data structure to compare against the expected one.
        :param subset:
            When true, any extra keys/values found in dictionaries will be ignored
            and assumed to be insignificant. Set to false for exact matching.
        :return:
            A comparison object that describes the element-wise differences between
            the observed data structure and its expectations.
        """
        pass
