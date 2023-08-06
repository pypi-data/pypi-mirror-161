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
  
# Examples

Print a list of available versions for a package:  
  
  ```
  from otlet.api import PackageObject
  
  pkg = PackageObject("pygame")
  print("All available versions for pygame:")
  for ver in pkg.releases:
      print(ver)
  ```  
 
Print a list of a dependency's dependencies:
  
  ```
  from otlet.api import PackageObject
  
  pkg = PackageObject("Sphinx")
  requests = pkg.dependencies[13]
  requests.populate()
  print("All dependencies of the 'Sphinx' dependency, 'requests':")
  for dep in requests.dependencies:
      print(dep.name)
  ```
# Development

If you plan to contribute to otlet and clone the repository, make sure you have installed the [Poetry dependency management system](https://python-poetry.org/), then run the following commands to set up your environment:

```
poetry install # to set up virtualenv, and install all dev dependencies
git config --local core.hooksPath .githooks/ # add otlet's hooks to your local repo config
```
