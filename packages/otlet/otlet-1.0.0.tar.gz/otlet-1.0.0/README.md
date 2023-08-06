<div align="center">
    <img src="https://commedesgarcons.s-ul.eu/Ht5pZjlN" alt="otlet readme image"><br>
    Zero-dependency, pure-python wrapper for the PyPI JSON Web API.

[![Documentation Status](https://readthedocs.org/projects/otlet/badge/?version=latest)](https://otlet.readthedocs.io/en/latest/?badge=latest)
[![license-mit](https://img.shields.io/pypi/l/otlet)](https://github.com/nhtnr/otlet/blob/main/LICENSE)
[![build-workflow](https://github.com/nhtnr/otlet/actions/workflows/pytest.yml/badge.svg?branch=main&event=push)](https://github.com/nhtnr/otlet/actions/workflows/pytest.yml)
[![github-issues](https://img.shields.io/github/issues/nhtnr/otlet)](https://github.com/nhtnr/otlet/issues)
[![github-pull-requests](https://img.shields.io/github/issues-pr/nhtnr/otlet)](https://github.com/nhtnr/otlet/pulls)
![pypi-python-versions](https://img.shields.io/pypi/pyversions/otlet)
[![pypi-package-version](https://img.shields.io/pypi/v/otlet)](https://pypi.org/project/otlet/)

</div>

# Installing

Otlet supports Python 3.6 and above, but at least Python 3.8 is recommended.

The simplest method is installing otlet from PyPI using pip:  
  
```pip install -U otlet```

It can also be installed from source using the [Poetry dependency management system](https://python-poetry.org/):  
  
```
# from root project directory

# build wheel from source and install
poetry build
cd dist && pip install ./path-to-otlet-wheel.whl

# install directly with pyproject.toml and masonry (poetry build API)
pip install .
```

# Development

If you plan to contribute to otlet and clone the repository, please run the following commands to set up your environment:

```
poetry install # to set up virtualenv, and install pytest and mypy
git config --local core.hooksPath .githooks/ # add otlet's hooks to your local repo config
```
