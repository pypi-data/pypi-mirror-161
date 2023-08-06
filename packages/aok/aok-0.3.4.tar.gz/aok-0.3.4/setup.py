# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aok', 'aok.comparisons']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1', 'toml>=0.10.2']

setup_kwargs = {
    'name': 'aok',
    'version': '0.3.4',
    'description': 'Complex dictionary comparisons to simplify testing.',
    'long_description': '# A-OK\n\n[![PyPI version](https://badge.fury.io/py/aok.svg)](https://pypi.org/project/aok/)\n[![build status](https://gitlab.com/rocket-boosters/a-ok/badges/main/pipeline.svg)](https://gitlab.com/rocket-boosters/a-ok/commits/main)\n[![coverage report](https://gitlab.com/rocket-boosters/a-ok/badges/main/coverage.svg)](https://gitlab.com/rocket-boosters/a-ok/commits/main)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-white)](https://gitlab.com/pycqa/flake8)\n[![Code style: mypy](https://img.shields.io/badge/code%20style-mypy-white)](http://mypy-lang.org/)\n[![PyPI - License](https://img.shields.io/pypi/l/aok)](https://pypi.org/project/aok/)\n\n*aok* is a library for simplifying the assertions of complex dictionary returns,\nwhich can be used within Python code or loaded via YAML files.\n\n```python\nimport aok\n\nimport my_application\n\n\ndef test_call():\n    """Should return the expected dictionary from my application call."""\n    result: dict = my_application.get_family("Jane Doe")\n    ok = aok.Okay({\n        "mother": {\n            "age": aok.greater_or_equal(50),\n            "full_name": aok.like("* Doe"),\n        },\n        "father": {\n            "age": aok.greater_or_equal(50),\n            "full_name": aok.like("* Doe"),\n        },\n        "younger_brother": {\n            "age": aok.less(10),\n            "full_name": aok.like("* Doe"),\n        }\n    })\n    \n    # Dictionary "result" must be an exact match with the ok expected values.\n    ok.assert_all(result)\n\n    # Dictionary "result" is asserted against ok expected values as a subset, such\n    # that other keys/values may exist within the "result" structure.\n    ok.assert_subset(result)\n```\n\nThe same thing can be archived from a YAML file:\n\n```yaml\nok: !aok\n  mother:\n    age: !aok.greater_or_equal 50\n    full_name: !aok.like \'* Doe\'\n  father:\n    age: !aok.greater_or_equal 50\n    full_name: !aok.like \'* Doe\'\n  younger_brother:\n    age: !aok.less 10\n    full_name: !aok.like \'* Doe\'\n```\n\nand this can be loaded into a test:\n\n```python\nimport aok\nimport yaml\nimport pathlib\n\nimport my_application\n\n\ndef test_call():\n    """Should return the expected dictionary from my application call."""\n    result: dict = my_application.get_family("Jane Doe")\n    data: dict = yaml.full_load(pathlib.Path("expectations.yaml").read_text())\n    ok: aok.Okay = data["ok"]\n    ok.assert_all(result)\n```\n\nIt is also possible to do a comparison on lists with `aok.OkayList` and the `!aok_list`\nclass replacing the `aok.Okay` and `!aok` values like shown in the example above.\n\nThe available comparators are:\n- `aok.anything()` will always succeed, no matter what the observed value is. \n- `aok.between(min, max)` must be greater than or equal to min and less than or equal\n  to the specified min and max values. This can be a numeric or string value.\n- `aok.equals(value)` must be an exact match between the values.\n- `aok.unequals(value)` must not be equal to the expected value.\n- `aok.greater(value)` must be greater than the specified value.\n- `aok.greater_or_equal(value)` must be greater than or equal to the specified value.\n- `aok.less(value)` must be less than the specified value.\n- `aok.less_or_equal(value)` must be less than or equal to the specified value.\n- `aok.contains(string_value)` must be a string that contains the specified substring \n   exactly.\n- `aok.not_contains(string_value)` must be a string that does not contain the exact\n   specified string value.\n- `aok.like(string_value)` string compares against case-insensitive, unix-shell-style\n   wildcard expressions, e.g. "foo*" would match "foo-bar".\n- `aok.not_like(string_vlaue)` string compares against case-insensitive,\n   unix-shell-style wildcard expressions, e.g. "*bar*", and expects not to find a match.\n- `aok.like_case(string_value)` string compares against case-sensitive, \n   unix-shell-style wildcard expressions, e.g. "Foo*" would match "Foo-Bar".\n- `aok.match(string_regex_pattern)` matches the string against the specified regex \n   pattern.\n- `aok.not_null(value)` must not be null/None, but can be anything else.\n- `aok.optional(value)` must equal the specified value or be null/None.\n- `aok.one_of(value)` must match one of the values in the specified list. Any of the\n- `aok.none_of(value)` must not match one of the values in the specified list. Any of\n   the list items can also be a comparator that will be negated.\n- `aok.json_dict(dict)` parses a JSON-serialized string attribute and compares it to\n   the dictionary/object in the same fashion as the `!aok` root object.\n- `aok.json_list(list)` parses a JSON-serialized string attribute nad compares it to\n   the list object in the same fashion as the `!aok_list` root object.\n',
    'author': 'Scott Ernst',
    'author_email': 'swernst@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/rocket-boosters/a-ok',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
