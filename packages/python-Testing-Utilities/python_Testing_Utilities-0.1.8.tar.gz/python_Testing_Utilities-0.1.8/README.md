# python_Testing_Utilities
[![Build Status](https://travis-ci.org/rmetcalf9/python_Testing_Utilities.svg?branch=master)](https://travis-ci.org/rmetcalf9/python_Testing_Utilities)
[![PyPI version](https://badge.fury.io/py/python_Testing_Utilities.svg)](https://badge.fury.io/py/python_Testing_Utilities)


Testing utilities for python apps


# Release process

````
USE CODERELEASE
````

If you get an error message reporting "dirty" versions can't be uploaded to pypi it means that you have uncommitted changes.


# installs to make a package:

pip install nose
pip install tox


pip install versioneer
###pip install wheel???

pip install virtualenv
pip install pipenv

run versioneer install in source tree

# Run tests
````
nosetests
````

````
pipenv shell
pipenv run tox
````

## Create pypi file

$HOME/.pypirc
````
[distutils]
index-servers=pypi

[pypi]
repository = https://pypi.python.org/pypi
username = <username>
password = <password>

````

If you leave password blank you will be prompted
