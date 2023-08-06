This document discusses setting up local development for this project on your own personal Linux box. 

## Install Dependencies 

It is wise to do development in an virtual environment.

    python3 -m venv venv
    source venv/bin/activate

Now dependencies can be installed!
For development, you should use the dependencies that are specified in `requirements.txt`:

    pip install -r requirements.txt

## Running from Source

To run this project from source code, we use the `--editable` flag with `pip install` against the locally downloaded repository.

    # run from the directory where setup.py lives
    pip install --editable .

This will install this project into your site-packages.
Using this feature, any changes you make in the source code will be reflected when testing the code!

## Dependency Management

We use `requirements.txt` to define all dependencies for development, while `setup.py` holds a *looser* list of package that are installed when the package is installed via pip.
This follows [general Python practices, (discussed on python.org)](https://packaging.python.org/discussions/install-requires-vs-requirements/#install-requires)

### Development Dependencies: `requirements.txt`

`requirements.txt` holds all of the development dependencies for this project.

If you make changes to dependencies, be sure to update requirements.txt.
The following command will update requirements.txt (and will correctly omit 'editable' packages).

    pip freeze | grep -v ^-e > requirements.txt

### Production Dependencies: `setup.py`

In `setup.py`, there is the **minimum** List of packages required for installation: `install_requires`.
This list should follow best practices, I.e.,

1. do consider pinning major version, e.g. `requests>=2,<3`,
2. do **NOT** pin specific minor or patch versions, and 
3. do **NOT** specify sub-dependencies.

#### Testing Production Dependencies

> The normal development workflow will install dependencies specified in `requirements.txt` -- here we omit that step so that we can test the setup.py 

Production dependencies outlined in `setup.py` **should be tested when they are created/updated**, to ensure the dependencies are sufficient.
Create a virtual environment specifically for this purpose:

    python3 -m venv venv-prod
    source venv-prod/bin/activate
    pip install --editable .

Ensure your package tools/tests work as expected using this `venv-prod`!

## Automated Testing

pytest is used to automatically testing this project.

Simply run the `pytest` CLI tool from the local directory to run all of the tests!

    $ pytest
    =========================== test session starts ============================
    platform linux -- Python 3.x.y, pytest-6.x.y, py-1.x.y, pluggy-1.x.y
    cachedir: $PYTHON_PREFIX/.pytest_cache
    ... omitted for brevity...

### What does `@pytest.mark.vcr()` mean?

We use [VCR.py](https://vcrpy.readthedocs.io/en/latest/) to enable reproducable end-to-end (e2e) testing of HTTP APIs.

To simplify usage of VCR.py, we leverage the [pytest-vcr package](https://pytest-vcr.readthedocs.io/en/latest/).
This package enables a simple decorator to be added to any e2e test case, which will then have a 'VCR.py cassette file' recorded containing a **replay** of the HTTP Requests that occurred during the initial test-run.

> TODO: Document how to rebuild cassettes.
