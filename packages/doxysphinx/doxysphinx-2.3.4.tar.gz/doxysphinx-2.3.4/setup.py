# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['doxysphinx', 'doxysphinx.utils']

package_data = \
{'': ['*'], 'doxysphinx': ['resources/*']}

install_requires = \
['click-log>=0.4.0,<0.5.0',
 'click>=8.1.3,<9.0.0',
 'json5>=0.9.8,<0.10.0',
 'lxml>=4.9.1,<5.0.0']

extras_require = \
{':sys_platform == "windows"': ['colorama>=0.4.5,<0.5.0']}

entry_points = \
{'console_scripts': ['doxysphinx = doxysphinx.cli:cli']}

setup_kwargs = {
    'name': 'doxysphinx',
    'version': '2.3.4',
    'description': 'Integrates doxygen html documentation with sphinx.',
    'long_description': '<!--\n=====================================================================================\n C O P Y R I G H T\n-------------------------------------------------------------------------------------\n Copyright (c) 2022 by Robert Bosch GmbH. All rights reserved.\n\n Author(s):\n - Markus Braun, :em engineering methods AG (contracted by Robert Bosch GmbH)\n - Nirmal Sasidharan, Robert Bosch Gmbh\n - Wolfgang Ulmer, Robert Bosch GmbH\n=====================================================================================\n-->\n\n<div align="center">\n\n<img src="https://raw.githubusercontent.com/boschglobal/doxysphinx/main/docs/resources/doxysphinx_logo.svg" alt="doxysphinx" width=500 />\n\n</div>\n\n---\n\n[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE.md)\n[![Pypi package](https://img.shields.io/pypi/v/doxysphinx)](https://pypi.org/project/doxysphinx/)\n[![supported Python versions](https://img.shields.io/pypi/pyversions/doxysphinx)](https://pypi.org/project/doxysphinx/)\n[![Build action: CI](https://github.com/boschglobal/doxysphinx/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/boschglobal/doxysphinx/actions/workflows/ci.yml)\n[![Build action: CD](https://github.com/boschglobal/doxysphinx/actions/workflows/cd.yml/badge.svg?tag=latest)](https://github.com/boschglobal/doxysphinx/actions/workflows/cd.yml)\n\nDoxysphinx is a [Doxygen](https://doxygen.nl) and [Sphinx](https://sphinx-doc.org) integration tool.\n\nIt is an easy-to-use cli tool and typically runs right after Doxygen generation.\nIt reuses the Doxygen generated HTML output and integrates it into Sphinx document generation.\nWith this, Doxysphinx supports all known Doxygen features and at the same time integrates well with the Sphinx output (for example, Sphinx-Themes, search etc.).\nDoxysphinx, also supports [restructured text (rST) annotations](https://github.com/boschglobal/doxysphinx/blob/main/docs/using_rst_in_doxygen.md) within C++ files.\n\nInternally, Doxysphinx creates an rST file for each (Doxygen) HTML file and includes the HTML using `.. raw:: html` directive.\nLater Sphinx picks up these rST files and creates an integrated documentation.\n\nCheck out Doxysphinx alternatives [here](https://github.com/boschglobal/doxysphinx/blob/main/docs/alternatives.md).\n\n## Links\n\n📚 [Doxysphinx Overview](https://boschglobal.github.io/doxysphinx)\n\n🚀 [Getting Started](https://boschglobal.github.io/doxysphinx/docs/getting_started.html)\n\n💻 [Developer Quickstart](https://boschglobal.github.io/doxysphinx/docs/dev_guide.html)\n\n🤖 [Releases](https://github.com/boschglobal/doxysphinx/releases)\n',
    'author': 'Nirmal Sasidharan',
    'author_email': 'nirmal.sasidharan@de.bosch.com',
    'maintainer': 'Nirmal Sasidharan',
    'maintainer_email': 'nirmal.sasidharan@de.bosch.com',
    'url': 'https://github.com/boschglobal/doxysphinx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
