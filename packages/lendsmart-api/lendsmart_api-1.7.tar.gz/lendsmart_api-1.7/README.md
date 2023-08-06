# lendsmart_api

*python*

The official python library for the [Lendsmart API v1](https://lendsmartlabs.postman.co)` in python.

**This library is currently in beta.**

[![PyPI](https://img.shields.io/pypi/v/lendsmart-api.svg)](https://pypi.python.org/pypi/lendsmart-api)
[![PyPI](https://img.shields.io/pypi/pyversions/lendsmart-api.svg)](https://pypi.python.org/pypi/lendsmart-api)

[https://badge.fury.io/py/lendsmart-api.svg](https://badge.fury.io/py/lendsmart-api)



## Pre reqs

- python 3

- install virtualenv using below command

```
    pip install virtualenv
```

## Activate virtual environment

```
    . ./venv/bin/activate
```

## Installation

```
    pip install lendsmart_api
```

# Usage

You will need the service account private key files to access Lendsmart.

Only a limited set of API is supported.

## Client

### Create client

```

```

### Update Document


```


```



# Building from Source


To build and install this package:

- Clone this repository

```

    cd core_api

    virtualenv venv

    ./setup.py install
```

# Testing individually

Make sure the `prereqs`, and `building from source` are complete

```

    cd lendsmart_python

    . venv/bin/activate

    python3 get_documents_test.py
```
# Local testing with lendsmart_api package
# Set environment path to your local file path in your python file

```
import sys
sys.path.append('/home/lendsmart/code/lendsmart/workspace/py_lscommon/core_api/')
```
# remove old package which is in virtual environment
```
rm -r /venv/lib/python3.8/site-packages/lendsmart_api
```
# Auto tests

Tests live in the ``tests`` directory.  When invoking tests, make sure you are
in the root directory of this project.  To run the full suite across all
supported python versions, use tox_:

```

   tox

```

Running tox also runs pylint and coverage reports.

The test suite uses fixtures stored as JSON in `test/fixtures`.  These files
contain sanitized JSON responses from the API - the file name is the URL called
to produce the response, replacing any slashes with underscores.

Test classes should extend `test.base.ClientBaseCase`.  This provides them
with `self.client`, a `LendsmartClient` object that is set up to work with
tests.  Importantly, any GET request made by this object will be mocked to
retrieve data from the test fixtures.  This includes lazy-loaded objects using
this client (and by extension related models).

When testing against requests other than GET requests, `self.mock_post` (and
equivalent methods for other HTTP verbs) can be used in a ``with`` block to
mock out the intended request type.  

[tox](http://tox.readthedocs.io)

# License

MIT

# Author

Lendsmart Inc, USA
