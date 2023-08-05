# Contributing

This page will walk you through how to start developing and contributing to the Myst Python Client Library.

## Setup

### Repository setup

First, you'll need to clone the repository from GitHub:

    $ git clone git@github.com:myst-ai/atrus.git

We use [`pyenv`](https://github.com/pyenv/pyenv) to manage Python runtime versions. If you don't already have it,
install it:

    $ brew install pyenv

Next, use `pyenv` to install the version of Python in [.python-version](.python-version) using `pyenv`:

    $ pyenv install $(cat .python-version)

We currently use [`pre-commit`](https://pre-commit.com) to configure hooks to run before committing to git. These hooks
run linters, auto-formatters, etc. so that we maintain consistent code style throughout the repository. To setup
`pre-commit` hooks, run the following command from the root of the repository:

    $ brew install pre-commit && pre-commit install

Note: By default, `pre-commit` will only run on staged files; however, you can force a re-run on all files using
`pre-commit run --all-files`.

### Installation

We use [`flit`](https://flit.readthedocs.io/en/latest/index.html) to manage development tasks such as building,
packaging, and distributing.. To install the `myst` Python package and begin developing, activate your virtualenv, then
install `flit` and then the repository code by running the following from the repository root:

    $ python -m pip install flit && flit install

By default, this installs the dev dependencies, so you can run tasks like lint, test, packaging, etc.

## Testing

### Running the tests locally

We currently use [`pytest`](https://pytest.org/):

    $ pytest

### Running the tests with `tox`

We use [`tox`](https://tox.readthedocs.io/en/latest/) to test compatibility with multiple Python versions and library
versions. Currently, we test compatibility with Python 3.7, 3.8, and 3.9.

To run packaging tests and unit tests using `tox`, run the following command from the root of the repository:

    $ tox

Tox caches previously initialized Python environments in the `.tox` hidden directory. To force `tox` to recreate these
environments, run:

    $ tox -r

### Generating test coverage reports

Generate a new code coverage report:

    $ coverage run -m pytest

View coverage report on command line:

    $ coverage report

Generate coverage HTML report and view in browser:

    $ coverage html && open htmlcov/index.html

Note that the `coverage` tool configuration can be edited in `.coveragerc`.

## OpenAPI Client Generation

Regenerate the OpenAPI client from schema with

    $ python tools/generate_openapi_client.py

which will overwrite any existing contents with updated Python model definitions and APIs.

### Debugging OpenAPI Client Generation

If you run into any mysterious errors while generating the OpenAPI client, you can enable "template debugging" in
PyCharm by following the directions [here](https://blog.jetbrains.com/pycharm/2017/06/template-debugging/). To
summarize, ensure that all `.jinja` files are correctly marked as the Jinja2 file type, and set the "Template language"
to "Jinja" under Preferences -> Languages & Frameworks -> Python Template Languages in PyCharm.

You should now be able to set breakpoints in the Jinja2 templates that PyCharm will recognize. This is particularly
helpful for setting log breakpoints – breakpoints that log values in the Jinja2 templates.

## Myst Python Client Library Release Checklist 🚀

NOTE: This assumes a freeze to the `main` branch for the duration of the release process. If and when this becomes an
obstacle, we can introduce a slight variant that involves a separate release branch.

- [ ] Create a release branch of the format release/vX.Y.Z (using [semver](https://semver.org/) conventions).
- [ ] Update Python package version in `pyproject.toml` to match the release branch version.
- [ ] Update the CHANGELOG.md file with release notes.
- [ ] Commit these changes to the release branch.
- [ ] Create pull request for release branch against the main branch.
- [ ] Kick off the `PyPi Deploy - Test` custom Github Action on the release branch and ensure it succeeds.
- [ ] Once approved, merge the version increment/changelog update branch (squash is okay).
- [ ] Create a new [release](https://github.com/myst-ai/atrus/releases/new) in GitHub off of the latest commit on `main`, adding the tag `vX.Y.Z` equal to the current value in the `pyproject.toml`. Autogenerate the release notes.
- [ ] Kick off the `PyPi Deploy` GitHub action against the release branch. This will initiate the deployment to PyPI.
- [ ] Double check that the new version of the `myst-alpha` package shows up on the
      [Myst PyPI Home Page](https://pypi.org/project/myst-alpha/) under "Release history"
- [ ] Run `pip install myst-alpha` in a new virtual environment and sanity check that the new release can be installed
      successfully.

### Testing PyPI Deployment

As referenced in the release checklist, we've also set up a custom action in Github Actions that can be run manually to
test the end-to-end packaging, distributing, and installation flow against the PyPI Test index server (a separate
instance of PyPI dedicated to testing).

You can kick off this pipeline through the GitHub "Actions" view. Click on "PyPI Deploy - Test", then click on "Run workflow" to begin the test deploy.

We highly recommend running this right before merging release branches into `main` as a last sanity check that the
release will result in a successful, bug-free distribution of `myst` being uploaded to PyPI. Note that PyPI Test acts
identically to PyPI and will also not allow packages to be updated in place without a version increment.

### Manual (not recommended)

If needed, you can also create and upload manual distributions of Atrus to PyPI. We don't foresee many instances when
this would be necessary, since all official releases and hotfixes will be automatically deployed by our
GitHub Actions script when the "Deploy" action is dispatched, but we're including this guide for reference.

Additionally, you can tell `flit` to use a different PyPI index server, which is useful when testing the end-to-end
packaging, distribution, and installation flow.

To create the sdist and wheel, simply run

    $ flit build

This will create two new distributions in the `dist/` directory (where `0.1.0` is replaced with the current version):

    - myst-0.1.0.tar.gz
    - myst-0.1.0-py3-none-any.whl

To upload to PyPI:

    $ flit publish

This will prompt you interactively for a username and password. An alternative is to configure your credentials in
`~/.pypirc` or using environment variables. Flit has some documentation on this
[here](https://flit.readthedocs.io/en/latest/upload.html).

**Remember:** Once you upload a version, it can't be updated in place so be sure to get this right!

PyPI recommends using an [API token](https://pypi.org/help/#apitoken) over a traditional username/password combination.

You can also specify a different target repository for upload by running first configuring

    $ flit publish --repository testpypi

where `testpypi` is the name of a repository configured in your `~/.pypirc`.
