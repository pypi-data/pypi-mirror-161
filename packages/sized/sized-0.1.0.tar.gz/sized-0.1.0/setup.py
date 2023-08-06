# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sized']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sized',
    'version': '0.1.0',
    'description': 'Sized Generators with Decorators',
    'long_description': "# sized\n\n[![Build](https://github.com/ionite34/sized/actions/workflows/build.yml/badge.svg)](https://github.com/ionite34/sized/actions/workflows/build.yml)\n[![codecov](https://codecov.io/gh/ionite34/sized/branch/main/graph/badge.svg)](https://codecov.io/gh/ionite34/sized)\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B31224%2Fgithub.com%2Fionite34%2Fsized.svg?type=shield)](https://app.fossa.com/projects/custom%2B31224%2Fgithub.com%2Fionite34%2Fsized?ref=badge_shield)\n\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/ionite34/sized/main.svg)](https://results.pre-commit.ci/latest/github/ionite34/sized/main)\n[![DeepSource](https://deepsource.io/gh/ionite34/sized.svg/?label=active+issues&show_trend=true&token=F69_eHULQKuPhzJHAa6XvCcH)](https://deepsource.io/gh/ionite34/sized/?ref=repository-badge)\n\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sized)](https://pypi.org/project/sized/)\n[![PyPI version](https://badge.fury.io/py/sized.svg)](https://pypi.org/project/sized/)\n\n### Sized Generators with Decorators\n\n## Why?\n- The `SizedGenerator` type provides a simple and robust way to keep track of iterations and max sizes for\ngenerators and iterators.\n- An issue with using normal Generators with long-running / multithread processes has been reporting\nprogress.\n- Here is an example of a standard `Generator` being wrapped with `tqdm`:\n\n```python\nfrom tqdm import tqdm\n\ndef gen():\n    n = 2\n    for _ in range(100):\n        n += (5 * 1 / n)\n        yield n\n\nfor x in tqdm(gen()):\n    pass\n\n# Output has no progress bar:\n> 100it [00:00, 1.00it/s]\n```\n\n- A solution would be to keep track of the total progress, but this gets messy if an iteration is\ninterrupted by user actions and the progress bar needs to continue.\n- Now with the `sized` decorator:\n\n```python\nfrom sized import sized\n\n@sized(100)\ndef s_gen():\n    n = 2\n    for _ in range(100):\n        n += (5 * 1 / n)\n        yield n\n\nfor x in tqdm(s_gen()):\n    pass\n\n# Now with a progress bar!\n> 100%|██████████| 100/100 [00:00<00:00, 1.00it/s]\n```\n\n- `SizedGenerator` will also track iterations called and reflect remaining length\n\n```python\ngen_instance = s_gen()\n\nlen(gen_instance) -> 100\n\nnext(gen_instance)\nnext(gen_instance)\n\nlen(gen_instance) -> 98\n```\n\n## Getting started\n\n### There are 2 main ways to create a `SizedGenerator`\n\n### 1. `@sized` decorator\n```python\nfrom sized import sized\n\n@sized(5)\ndef gen():\n    yield ...\n```\n\n\n### 2. `SizedGenerator` constructor\n```python\nfrom sized import SizedGenerator\n\ngen = SizedGenerator((x ** 2 for x in range(10)), 10)\n```\n\n## Additional Info\n\n- The `size` argument can be either an `int`, `Sized` object, or a callable accepting a dictionary of\narguments and keyword-arguments, returning an `int` or `Sized` object.\n\n```python\n@sized(15) # int\ndef gen():\n    for i in range(15):\n        yield i ** 2\n```\n```python\nls = [1, 4, 5]\n\n@sized(ls) # `Sized` objects will have len(obj) called automatically\ndef gen():\n    for i in ls:\n        yield i ** 2\n```\n```python\n@sized(lambda x: x['some_arg']) # Callable using keyword argument, returning `Sized`\ndef gen(arg = None):\n    for i in arg:\n        yield i ** 2\n```\n```python\n@sized(lambda x: 2 * len(x['1'])) # Callable using positional argument, returning `int`\ndef gen(arg_0, arg_1):\n    for _ in range(2):\n        for i in arg_1:\n            yield i ** 2 + arg_0\n```\n\n## License\nThe code in this project is released under the [MIT License](LICENSE).\n\n[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B31224%2Fgithub.com%2Fionite34%2Fsized.svg?type=large)](https://app.fossa.com/projects/custom%2B31224%2Fgithub.com%2Fionite34%2Fsized?ref=badge_large)\n",
    'author': 'ionite34',
    'author_email': 'dev@ionite.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ionite34/sized',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<3.12',
}


setup(**setup_kwargs)
