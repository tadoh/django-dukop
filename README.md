# dukop.dk

[![Build Status](https://travis-ci.com/dukop/django-dukop.svg?branch=master)](https://travis-ci.com/dukop/django-dukop)

Collaborate calendar for Copenhagen area

## Requirements

* Python 3.6+ (is already on your system)
* SQLite3 (development)
  * `sudo apt install libsqlite3-dev`
* Postgres (deployment)

Other requirements are specified as Python packages in the *Quickstart* below and will be installed in a *virtual environment*.

## Quickstart

Install the project and the development dependencies into a [virtual environment](https://docs.python.org/3.7/tutorial/venv.html):

```console
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install --editable ".[dev]"
./manage.py migrate
./manage.py createsuperuser
```

The development environment is now ready with an empty database and a single admin user. To run the server and access it from your browser, use the `runserver` command:

```console
./manage.py runserver
```

## Running tests

More details to come, but for now, just open a PR and wait for Travis or run this:

```console
pytest
```

## Starting a New App

First create a new directory in the `apps` directory:

```console
mkdir src/dukop/apps/name
```

Then pass the path to the new directory to the [startapp](https://docs.djangoproject.com/en/2.1/ref/django-admin/#django-admin-startapp) command:

```console
./manage.py startapp name src/dukop/apps/name
```
