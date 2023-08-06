# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autohooks', 'autohooks.plugins.pylint']

package_data = \
{'': ['*']}

modules = \
['CHANGELOG', 'RELEASE', 'poetry']
install_requires = \
['autohooks>=2.2.0', 'pylint>=2.8.3,<3.0.0']

setup_kwargs = {
    'name': 'autohooks-plugin-pylint',
    'version': '22.8.0',
    'description': 'An autohooks plugin for python code linting via pylint',
    'long_description': '![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_new-logo_horizontal_rgb_small.png)\n\n# autohooks-plugin-pylint\n\n[![PyPI release](https://img.shields.io/pypi/v/autohooks-plugin-pylint.svg)](https://pypi.org/project/autohooks-plugin-pylint/)\n\nAn [autohooks](https://github.com/greenbone/autohooks) plugin for python code\nlinting via [pylint](https://github.com/PyCQA/pylint).\n\n## Installation\n\n### Install using pip\n\nYou can install the latest stable release of autohooks-plugin-pylint from the\nPython Package Index using [pip](https://pip.pypa.io/):\n\n    pip install autohooks-plugin-pylint\n\nNote the `pip` refers to the Python 3 package manager. In a environment where\nPython 2 is also available the correct command may be `pip3`.\n\n### Install using poetry\n\nIt is highly encouraged to use [poetry](https://python-poetry.org) for\nmaintaining your project\'s dependencies. Normally autohooks-plugin-pylint is\ninstalled as a development dependency.\n\n    poetry install\n\n## Usage\n\nTo activate the pylint autohooks plugin please add the following setting to your\n*pyproject.toml* file.\n\n```toml\n[tool.autohooks]\npre-commit = ["autohooks.plugins.pylint"]\n```\n\nBy default, autohooks plugin pylint checks all files with a *.py* ending. If\nonly files in a sub-directory or files with different endings should be\nformatted, just add the following setting:\n\n```toml\n[tool.autohooks]\npre-commit = ["autohooks.plugins.pylint"]\n\n[tool.autohooks.plugins.pylint]\ninclude = [\'foo/*.py\', \'*.foo\']\n```\n\nBy default, autohooks plugin pylint executes pylint without any arguments and\npylint settings are loaded from the *.pylintrc* file in the root directory of\ngit repository. To change specific settings or to define a different pylint rc\nfile the following plugin configuration can be used:\n\n```toml\n[tool.autohooks]\npre-commit = ["autohooks.plugins.pylint"]\n\n[tool.autohooks.plugins.pylint]\narguments = ["--rcfile=/path/to/pylintrc", "-s", "n"]\n```\n\n## Maintainer\n\nThis project is maintained by [Greenbone Networks GmbH](https://www.greenbone.net/).\n\n## Contributing\n\nYour contributions are highly appreciated. Please\n[create a pull request](https://github.com/greenbone/autohooks-plugin-pylint/pulls)\non GitHub. Bigger changes need to be discussed with the development team via the\n[issues section at GitHub](https://github.com/greenbone/autohooks-plugin-pylint/issues)\nfirst.\n\n## License\n\nCopyright (C) 2019 - 2022 [Greenbone Networks GmbH](https://www.greenbone.net/)\n\nLicensed under the [GNU General Public License v3.0 or later](LICENSE).\n',
    'author': 'Greenbone Networks GmbH',
    'author_email': 'info@greenbone.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/greenbone/autohooks-plugin-pylint',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
