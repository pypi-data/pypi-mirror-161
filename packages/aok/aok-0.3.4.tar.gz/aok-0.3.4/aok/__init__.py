"""Complex dictionary comparisons to simplify testing."""
import pathlib as _pathlib
from importlib import metadata as _metadata

import toml as _toml

from aok._definitions import Comparator  # noqa: F401
from aok._definitions import Comparison  # noqa: F401
from aok._operations import to_comparator  # noqa
from aok._types import ArbitraryDict  # noqa: F401
from aok._types import ArbitraryList  # noqa: F401
from aok._types import OkayRoot  # noqa: F401
from aok.comparisons import Anything  # noqa: F401
from aok.comparisons import Between  # noqa: F401
from aok.comparisons import Contains  # noqa: F401
from aok.comparisons import Dict  # noqa: F401
from aok.comparisons import Equals  # noqa: F401
from aok.comparisons import Greater  # noqa: F401
from aok.comparisons import GreaterOrEqual  # noqa: F401
from aok.comparisons import JsonList  # noqa: F401
from aok.comparisons import Less  # noqa: F401
from aok.comparisons import LessOrEqual  # noqa: F401
from aok.comparisons import Like  # noqa: F401
from aok.comparisons import LikeCase  # noqa: F401
from aok.comparisons import List  # noqa: F401
from aok.comparisons import Match  # noqa: F401
from aok.comparisons import NoneOf  # noqa: F401
from aok.comparisons import NotContains  # noqa: F401
from aok.comparisons import NotLike  # noqa: F401
from aok.comparisons import NotNull  # noqa: F401
from aok.comparisons import Okay  # noqa: F401
from aok.comparisons import OkayList  # noqa: F401
from aok.comparisons import OneOf  # noqa: F401
from aok.comparisons import Optional  # noqa: F401
from aok.comparisons import StrictList  # noqa: F401
from aok.comparisons import Tuple  # noqa: F401
from aok.comparisons import Unequals  # noqa: F401
from aok.comparisons import anything  # noqa: F401
from aok.comparisons import between  # noqa: F401
from aok.comparisons import contains  # noqa: F401
from aok.comparisons import equals  # noqa: F401
from aok.comparisons import greater  # noqa: F401
from aok.comparisons import greater_or_equal  # noqa: F401
from aok.comparisons import json_list  # noqa: F401
from aok.comparisons import less  # noqa: F401
from aok.comparisons import less_or_equal  # noqa: F401
from aok.comparisons import like  # noqa: F401
from aok.comparisons import like_case  # noqa: F401
from aok.comparisons import match  # noqa: F401
from aok.comparisons import none_of  # noqa: F401
from aok.comparisons import not_contains  # noqa: F401
from aok.comparisons import not_like  # noqa: F401
from aok.comparisons import not_null  # noqa: F401
from aok.comparisons import one_of  # noqa: F401
from aok.comparisons import optional  # noqa: F401
from aok.comparisons import unequals  # noqa: F401

try:
    __version__ = _metadata.version(__package__)
except _metadata.PackageNotFoundError:  # pragma: no-cover
    # If the package is not installed such that it has distribution metadata
    # fallback to loading the version from the pyproject.toml file.
    __version__ = _toml.loads(
        _pathlib.Path(__file__).parent.parent.joinpath("pyproject.toml").read_text()
    )["tool"]["poetry"]["version"]
