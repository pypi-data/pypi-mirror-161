import typing

from aok import comparisons
from aok import _definitions


def to_comparator(value: typing.Any) -> "_definitions.Comparator":
    """
    Convert the value to a default comparator if not already one.

    If the value is already a comparator, it is returned unchanged.
    """
    if isinstance(value, _definitions.Comparator):
        return value
    elif isinstance(value, dict):
        return comparisons.Dict(value)
    elif isinstance(value, list):
        return comparisons.List(value)
    elif isinstance(value, tuple):
        return comparisons.Tuple(value)

    return comparisons.Equals(value)


def cast_compatible(
    expectation_value: typing.Any,
    observed_value: typing.Any,
) -> typing.Any:
    """Casts by compatible type, which is limited."""
    ex = expectation_value
    ob = observed_value

    if isinstance(ob, int) and isinstance(ex, str):
        return int(ex)
    elif isinstance(ob, float) and isinstance(ex, str):
        return float(ex)
    elif isinstance(ob, bool) and ex in ("true", "false"):
        return ex == "true"

    return ex
