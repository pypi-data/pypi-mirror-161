# A-OK

[![PyPI version](https://badge.fury.io/py/aok.svg)](https://pypi.org/project/aok/)
[![build status](https://gitlab.com/rocket-boosters/a-ok/badges/main/pipeline.svg)](https://gitlab.com/rocket-boosters/a-ok/commits/main)
[![coverage report](https://gitlab.com/rocket-boosters/a-ok/badges/main/coverage.svg)](https://gitlab.com/rocket-boosters/a-ok/commits/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-white)](https://gitlab.com/pycqa/flake8)
[![Code style: mypy](https://img.shields.io/badge/code%20style-mypy-white)](http://mypy-lang.org/)
[![PyPI - License](https://img.shields.io/pypi/l/aok)](https://pypi.org/project/aok/)

*aok* is a library for simplifying the assertions of complex dictionary returns,
which can be used within Python code or loaded via YAML files.

```python
import aok

import my_application


def test_call():
    """Should return the expected dictionary from my application call."""
    result: dict = my_application.get_family("Jane Doe")
    ok = aok.Okay({
        "mother": {
            "age": aok.greater_or_equal(50),
            "full_name": aok.like("* Doe"),
        },
        "father": {
            "age": aok.greater_or_equal(50),
            "full_name": aok.like("* Doe"),
        },
        "younger_brother": {
            "age": aok.less(10),
            "full_name": aok.like("* Doe"),
        }
    })
    
    # Dictionary "result" must be an exact match with the ok expected values.
    ok.assert_all(result)

    # Dictionary "result" is asserted against ok expected values as a subset, such
    # that other keys/values may exist within the "result" structure.
    ok.assert_subset(result)
```

The same thing can be archived from a YAML file:

```yaml
ok: !aok
  mother:
    age: !aok.greater_or_equal 50
    full_name: !aok.like '* Doe'
  father:
    age: !aok.greater_or_equal 50
    full_name: !aok.like '* Doe'
  younger_brother:
    age: !aok.less 10
    full_name: !aok.like '* Doe'
```

and this can be loaded into a test:

```python
import aok
import yaml
import pathlib

import my_application


def test_call():
    """Should return the expected dictionary from my application call."""
    result: dict = my_application.get_family("Jane Doe")
    data: dict = yaml.full_load(pathlib.Path("expectations.yaml").read_text())
    ok: aok.Okay = data["ok"]
    ok.assert_all(result)
```

It is also possible to do a comparison on lists with `aok.OkayList` and the `!aok_list`
class replacing the `aok.Okay` and `!aok` values like shown in the example above.

The available comparators are:
- `aok.anything()` will always succeed, no matter what the observed value is. 
- `aok.between(min, max)` must be greater than or equal to min and less than or equal
  to the specified min and max values. This can be a numeric or string value.
- `aok.equals(value)` must be an exact match between the values.
- `aok.unequals(value)` must not be equal to the expected value.
- `aok.greater(value)` must be greater than the specified value.
- `aok.greater_or_equal(value)` must be greater than or equal to the specified value.
- `aok.less(value)` must be less than the specified value.
- `aok.less_or_equal(value)` must be less than or equal to the specified value.
- `aok.contains(string_value)` must be a string that contains the specified substring 
   exactly.
- `aok.not_contains(string_value)` must be a string that does not contain the exact
   specified string value.
- `aok.like(string_value)` string compares against case-insensitive, unix-shell-style
   wildcard expressions, e.g. "foo*" would match "foo-bar".
- `aok.not_like(string_vlaue)` string compares against case-insensitive,
   unix-shell-style wildcard expressions, e.g. "*bar*", and expects not to find a match.
- `aok.like_case(string_value)` string compares against case-sensitive, 
   unix-shell-style wildcard expressions, e.g. "Foo*" would match "Foo-Bar".
- `aok.match(string_regex_pattern)` matches the string against the specified regex 
   pattern.
- `aok.not_null(value)` must not be null/None, but can be anything else.
- `aok.optional(value)` must equal the specified value or be null/None.
- `aok.one_of(value)` must match one of the values in the specified list. Any of the
- `aok.none_of(value)` must not match one of the values in the specified list. Any of
   the list items can also be a comparator that will be negated.
- `aok.json_dict(dict)` parses a JSON-serialized string attribute and compares it to
   the dictionary/object in the same fashion as the `!aok` root object.
- `aok.json_list(list)` parses a JSON-serialized string attribute nad compares it to
   the list object in the same fashion as the `!aok_list` root object.
