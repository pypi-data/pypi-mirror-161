# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snakecamel']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'snakecamel',
    'version': '0.1.0',
    'description': 'An easy-to-use package to convert to camelCase or snake_case',
    'long_description': '# snakecamel\n\n[![Test - pytest](https://github.com/lysnikolaou/snakecamel/actions/workflows/test.yml/badge.svg)](https://github.com/lysnikolaou/snakecamel/actions/workflows/test.yml)\n[![codecov](https://codecov.io/gh/lysnikolaou/snakecamel/branch/main/graph/badge.svg?token=1VWY4JCAWS)](https://codecov.io/gh/lysnikolaou/snakecamel)\n\nA small utility to camelize (convert to camel-case) or snakeize (convert to snake-case) any object.\n\nThis is a very early-stage project & for the time-being is only there as a personal utility.\n\n## Usage\n\n```python\nimport snakecamel\n>>> snakecamel.camelize("simple_string")\n\'simpleString\n>>> snakecamel.snakeize("simpleString")\n\'simple_string\'\n```\n\n### General notes\n\n1. The library is designed to be very forgiving. It does not raise upon encountering an unknown type, it\n   just skips it. This way, you can pass arbitrary objects to it & everything that can be camelized/snakeized,\n   will be.\n\n```python\n>>> import snakecamel\n>>> snakecamel.camelize(50)\n50\n>>> from datetime import date\n>>> snakecamel.camelize({"hello_world": "hello_world", 50: 50, date.today(): "today"})\n{\'helloWorld\': \'hello_world\', 50: 50, datetime.date(2022, 7, 31): \'today\'}\n```\n\n2. The library will try to re-construct the type you pass to it, so that if you pass\n   different kinds of iterables, you\'ll get the same type returned. Unfortunately, that still\n   does not work with mappings.\n\n```python\n>>> import snakecamel\n>>> snakecamel.camelize(["simple_string"])\n[\'simpleString\']\n>>> snakecamel.camelize({"simple_string"})\n{\'simpleString\'}\n>>> snakecamel.camelize(("simple_string",))\n(\'simpleString\',)\n>>> snakecamel.camelize("simple_string")\n\'simpleString\'\n```\n\n3. When camelizing/snakeizing mappings, you can choose to do so with keys only or keys & values.\n\n```python\n>>> import snakecamel\n>>> snakecamel.camelize({"simple_key": "simple_value"})\n{\'simpleKey\': \'simple_value\'}\n>>> snakecamel.camelize({"simple_key": "simple_value"}, camelize_mapping_values=True)\n{\'simpleKey\': \'simpleValue\'}\n```\n\n4. You can shoose between capitalized or non-capitalized camel case.\n\n```python\n>>> import snakecamel\n>>> snakecamel.camelize("simple_string")\n\'simpleString\'\n>>> snakecamel.camelize("simple_string", capitalized=True)\n\'SimpleString\'\n```\n\nWhen snakeizing, you _need_ to pass `capitalized=True`, if you want the first letter of a\ncapitalized camel-case word to be lowercased.\n\n```python\n>>> snakecamel.snakeize("simpleString")\n\'simple_string\'\n>>> snakecamel.snakeize("simpleString", capitalized=True)\n\'simple_string\'\n>>> snakecamel.snakeize("SimpleString")\n\'Simple_string\'\n>>> snakecamel.snakeize("SimpleString", capitalized=True)\n\'simple_string\'\n```\n\n5. When camelizing, you can choose whether you\'re stripping leading/trailing underscores or not.\n\n```python\nimport snakecamel\n>>> import snakecamel\n>>> snakecamel.camelize("_simple_string_")\n\'_simpleString_\'\n>>> snakecamel.camelize("_simple_string_", strip_underscores=True)\n\'simpleString\'\n```\n',
    'author': 'Lysandros Nikolaou',
    'author_email': 'lisandrosnik@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lysnikolaou/snakecamel',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
