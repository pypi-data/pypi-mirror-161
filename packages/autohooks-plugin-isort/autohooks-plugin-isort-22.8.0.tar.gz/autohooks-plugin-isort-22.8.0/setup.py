# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autohooks', 'autohooks.plugins.isort']

package_data = \
{'': ['*']}

modules = \
['CHANGELOG', 'RELEASE', 'poetry']
install_requires = \
['autohooks-plugin-black>=22.7.0',
 'autohooks-plugin-pylint>=21.6.0',
 'autohooks>=21.6.0',
 'isort>=5.8.0,<6.0.0']

setup_kwargs = {
    'name': 'autohooks-plugin-isort',
    'version': '22.8.0',
    'description': 'An autohooks plugin for python code formatting via isort',
    'long_description': '![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_new-logo_horizontal_rgb_small.png)\n\n# autohooks-plugin-isort\n\n[![PyPI release](https://img.shields.io/pypi/v/autohooks-plugin-isort.svg)](https://pypi.org/project/autohooks-plugin-isort/)\n\nAn [autohooks](https://github.com/greenbone/autohooks) plugin for Python code\nformatting via [isort](https://github.com/timothycrosley/isort).\n\n## Installation\n\n### Install using pip\n\nYou can install the latest stable release of autohooks-plugin-isort from the\nPython Package Index using [pip](https://pip.pypa.io/):\n\n    python3 -m pip install autohooks-plugin-isort\n\n### Install using poetry\n\nIt is highly encouraged to use [poetry](https://python-poetry.org) for\nmaintaining your project\'s dependencies. Normally autohooks-plugin-isort is\ninstalled as a development dependency.\n\n    poetry add --dev autohooks-plugin-isort\n\n    poetry install\n\n## Usage\n\nTo activate the isort autohooks plugin please add the following setting to your\n*pyproject.toml* file.\n\n```toml\n[tool.autohooks]\npre-commit = ["autohooks.plugins.isort"]\n```\n\nBy default, autohooks plugin isort checks all files with a *.py* ending. If only\nthe imports of files in a sub-directory or files with different endings should\nbe sorted, just add the following setting:\n\n```toml\n[tool.autohooks]\npre-commit = ["autohooks.plugins.isort"]\n\n[tool.autohooks.plugins.isort]\ninclude = [\'foo/*.py\', \'*.foo\']\n```\n\nWhen using `autohooks-plugins-isort` in combination with\n[autohooks-plugin-black](https://github.com/greenbone/autohooks-plugin-black),\nthe following configuration is recommended to ensure a consistent formatting:\n\n```toml\n[tool.isort]\nprofile = "black"\n```\n\n## Maintainer\n\nThis project is maintained by [Greenbone Networks GmbH](https://www.greenbone.net/).\n\n## Contributing\n\nYour contributions are highly appreciated. Please\n[create a pull request](https://github.com/greenbone/autohooks-plugin-isort/pulls)\non GitHub. Bigger changes need to be discussed with the development team via the\n[issues section at GitHub](https://github.com/greenbone/autohooks-plugin-isort/issues)\nfirst.\n\n## License\n\nCopyright (C) 2019 - 2022 [Greenbone Networks GmbH](https://www.greenbone.net/)\n\nLicensed under the [GNU General Public License v3.0 or later](LICENSE).\n',
    'author': 'Greenbone Networks GmbH',
    'author_email': 'info@greenbone.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/greenbone/autohooks-plugin-isort',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
