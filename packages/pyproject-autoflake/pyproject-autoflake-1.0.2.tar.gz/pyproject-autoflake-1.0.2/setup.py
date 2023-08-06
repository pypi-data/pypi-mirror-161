# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyproject_autoflake']

package_data = \
{'': ['*']}

install_requires = \
['autoflake', 'toml>=0.10.1']

entry_points = \
{'console_scripts': ['pautoflake = pyproject_autoflake.pautoflake:main']}

setup_kwargs = {
    'name': 'pyproject-autoflake',
    'version': '1.0.2',
    'description': 'pyproject-autoflake (pautoflake), a monkey patching wrapper to connect autoflake with pyproject.toml configuration.',
    'long_description': '# pyproject-autoflake\n\n[![PyPI version](https://badge.fury.io/py/pyproject-autoflake.svg)](https://badge.fury.io/py/pyproject-autoflake) [![Python Versions](https://img.shields.io/pypi/pyversions/pyproject-autoflake.svg)](https://pypi.org/project/pyproject-autoflake/)\n\n**pyproject-autoflake** (**pautoflake**), a monkey patching wrapper to connect [autoflake](https://github.com/myint/autoflake) with pyproject.toml configuration.\n\n## Motivation\n\nThe original autoflake does not support configuration files such as pyproject.toml.\nThis is slightly inconvenient for modern Python development.\n\npautoflake is a thin wrapper library that calls autoflake with a configuration read from pyproject.toml.\n\npyproject-autoflake is inspired by [pyproject-flake8](https://github.com/csachs/pyproject-flake8). Many thanks! 😉\n\n## Installation\n\n### pip\n\n```sh\npip install pyproject-autoflake\n```\n\n### poetry\n\n```sh\npoetry add -D pyproject-autoflake\n```\n\n## Usage\n\nAt first, you add `[tool.autoflake]` in your pyproject.toml.\n\n```toml\n# pyproject.toml\n\n...\n\n[tool.autoflake]\n# return error code if changes are needed\ncheck = false\n# make changes to files instead of printing diffs\nin-place = true\n# drill down directories recursively\nrecursive = true\n# exclude file/directory names that match these comma-separated globs\nexclude = "<GLOBS>"\n# by default, only unused standard library imports are removed; specify a comma-separated list of additional\n# modules/packages\nimports = "<IMPORTS>"\n# expand wildcard star imports with undefined names; this only triggers if there is only one star import in\n# the file; this is skipped if there are any uses of `__all__` or `del` in the file\nexpand-star-imports = true\n# remove all unused imports (not just those from the standard library)\nremove-all-unused-imports = true\n# exclude __init__.py when removing unused imports\nignore-init-module-imports = true\n# remove all duplicate keys in objects\nremove-duplicate-keys = true\n# remove unused variables\nremove-unused-variables = true\n# print more verbose logs (larger numbers are more verbose)\nverbose = 0\n\n...\n\n```\n\nSecond, you call **p**autoflake.\n\n```bash\npautoflake sample.py\n```\n\n## License\n\n[MIT License](./LICENSE)\n',
    'author': 'quwac',
    'author_email': '53551867+quwac@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/quwac/pyproject-autoflake',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
