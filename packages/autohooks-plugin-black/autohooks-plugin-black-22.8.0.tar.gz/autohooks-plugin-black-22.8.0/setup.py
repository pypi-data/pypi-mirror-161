# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autohooks', 'autohooks.plugins.black']

package_data = \
{'': ['*']}

modules = \
['CHANGELOG', 'RELEASE', 'poetry']
install_requires = \
['autohooks>=21.6.0', 'black>=20.8']

setup_kwargs = {
    'name': 'autohooks-plugin-black',
    'version': '22.8.0',
    'description': 'An autohooks plugin for python code formatting via black',
    'long_description': '![Greenbone Logo](https://www.greenbone.net/wp-content/uploads/gb_new-logo_horizontal_rgb_small.png)\n\n# autohooks-plugin-black\n\n[![PyPI release](https://img.shields.io/pypi/v/autohooks-plugin-black.svg)](https://pypi.org/project/autohooks-plugin-black/)\n\nAn [autohooks](https://github.com/greenbone/autohooks) plugin for python code\nformatting via [black](https://github.com/ambv/black).\n\n## Installation\n\n### Install using pip\n\nYou can install the latest stable release of autohooks-plugin-black from the\nPython Package Index using [pip](https://pip.pypa.io/):\n\n    pip install autohooks-plugin-black\n\nNote the `pip` refers to the Python 3 package manager. In a environment where\nPython 2 is also available the correct command may be `pip3`.\n\n### Install using poetry\n\nIt is highly encouraged to use [poetry](https://python-poetry.org) for\nmaintaining your project\'s dependencies. Normally autohooks-plugin-black is\ninstalled as a development dependency.\n\n    poetry add --dev autohooks-plugin-black\n\n## Usage\n\nTo activate the black autohooks plugin please add the following setting to your\n*pyproject.toml* file.\n\n```toml\n[tool.autohooks]\npre-commit = ["autohooks.plugins.black"]\n```\n\nBy default, autohooks plugin black checks all files with a *.py* ending. If only\nfiles in a sub-directory or files with different endings should be formatted,\njust add the following setting:\n\n```toml\n[tool.autohooks]\npre-commit = ["autohooks.plugins.black"]\n\n[tool.autohooks.plugins.black]\ninclude = [\'foo/*.py\', \'*.foo\']\n```\n\nAlso by default, autohooks plugin black executes black with the `-q` argument.\nIf e.g. the generated patch should be shown the following setting can be used:\n\n```toml\n[tool.autohooks]\npre-commit = ["autohooks.plugins.black"]\n\n[tool.autohooks.plugins.black]\narguments = ["-q", "--diff"]\n```\n\n## Maintainer\n\nThis project is maintained by [Greenbone Networks GmbH](https://www.greenbone.net/).\n\n## Contributing\n\nYour contributions are highly appreciated. Please\n[create a pull request](https://github.com/greenbone/autohooks-plugin-black/pulls)\non GitHub. Bigger changes need to be discussed with the development team via the\n[issues section at GitHub](https://github.com/greenbone/autohooks-plugin-black/issues)\nfirst.\n\n## License\n\nCopyright (C) 2019 [Greenbone Networks GmbH](https://www.greenbone.net/)\n\nLicensed under the [GNU General Public License v3.0 or later](LICENSE).\n',
    'author': 'Greenbone Networks GmbH',
    'author_email': 'info@greenbone.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/greenbone/autohooks-plugin-black',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
