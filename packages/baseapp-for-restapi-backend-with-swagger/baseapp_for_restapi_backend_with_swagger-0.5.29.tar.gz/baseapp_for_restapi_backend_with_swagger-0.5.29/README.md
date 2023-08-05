
# baseapp_for_restapi_backend_with_swagger

[![Build Status](https://travis-ci.org/rmetcalf9/baseapp_for_restapi_backend_with_swagger.svg?branch=master)](https://travis-ci.org/rmetcalf9/baseapp_for_restapi_backend_with_swagger)
[![PyPI version](https://badge.fury.io/py/baseapp_for_restapi_backend_with_swagger.svg)](https://badge.fury.io/py/baseapp_for_restapi_backend_with_swagger)


Python package which provides a base application class for an app with a restapi backend that provides a swagger


# Release process

Use coderelease

(Common bug: droid-sans.css won't load - see RESTPLUSDEPENDANCY.md for a possible cause)

# Information on building a python package

https://www.youtube.com/watch?v=4fzAMdLKC5k


Versioneer notes: https://github.com/warner/python-versioneer/blob/master/INSTALL.md

# installs to make a package:

pip install nose
pip install tox


pip install versioneer
###pip install wheel???

pip install virtualenv
pip install pipenv

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
