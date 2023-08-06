# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['otlet', 'otlet.packaging', 'otlet.packaging.version']

package_data = \
{'': ['*']}

extras_require = \
{'cli:python_version >= "3.7" and python_version < "4.0"': ['otlet-cli>=1.0.0,<2.0.0'],
 'docs': ['Sphinx>=4.5.0,<5.0.0', 'sphinx-rtd-theme>=1.0.0,<2.0.0']}

setup_kwargs = {
    'name': 'otlet',
    'version': '1.0.0.post1',
    'description': 'Zero-dependency, pure-python wrapper for the PyPI JSON Web API',
    'long_description': '<div align="center">\n    <img src="https://commedesgarcons.s-ul.eu/Ht5pZjlN" alt="otlet readme image"><br>\n    Zero-dependency, pure-python wrapper for the PyPI JSON Web API.\n\n[![Documentation Status](https://readthedocs.org/projects/otlet/badge/?version=latest)](https://otlet.readthedocs.io/en/latest/?badge=latest)\n[![license-mit](https://img.shields.io/pypi/l/otlet)](https://github.com/nhtnr/otlet/blob/main/LICENSE)\n[![build-workflow](https://github.com/nhtnr/otlet/actions/workflows/pytest.yml/badge.svg?branch=main&event=push)](https://github.com/nhtnr/otlet/actions/workflows/pytest.yml)\n[![github-issues](https://img.shields.io/github/issues/nhtnr/otlet)](https://github.com/nhtnr/otlet/issues)\n[![github-pull-requests](https://img.shields.io/github/issues-pr/nhtnr/otlet)](https://github.com/nhtnr/otlet/pulls)\n![pypi-python-versions](https://img.shields.io/pypi/pyversions/otlet)\n[![pypi-package-version](https://img.shields.io/pypi/v/otlet)](https://pypi.org/project/otlet/)\n\n</div>\n\n# Installing\n\nOtlet supports Python 3.6 and above, but at least Python 3.8 is recommended.\n\nThe simplest method is installing otlet from PyPI using pip:  \n  \n```pip install -U otlet```\n  \n# Examples\n\nPrint a list of available versions for a package:  \n  \n  ```\n  from otlet.api import PackageObject\n  \n  pkg = PackageObject("pygame")\n  print("All available versions for pygame:")\n  for ver in pkg.releases:\n      print(ver)\n  ```  \n \nPrint a list of a dependency\'s dependencies:\n  \n  ```\n  from otlet.api import PackageObject\n  \n  pkg = PackageObject("Sphinx")\n  requests = pkg.dependencies[13]\n  requests.populate()\n  print("All dependencies of the \'Sphinx\' dependency, \'requests\':")\n  for dep in requests.dependencies:\n      print(dep.name)\n  ```\n# Development\n\nIf you plan to contribute to otlet and clone the repository, make sure you have installed the [Poetry dependency management system](https://python-poetry.org/), then run the following commands to set up your environment:\n\n```\npoetry install # to set up virtualenv, and install all dev dependencies\ngit config --local core.hooksPath .githooks/ # add otlet\'s hooks to your local repo config\n```\n',
    'author': 'Noah Tanner (nhtnr)',
    'author_email': 'noahtnr@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nhtnr/otlet',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
