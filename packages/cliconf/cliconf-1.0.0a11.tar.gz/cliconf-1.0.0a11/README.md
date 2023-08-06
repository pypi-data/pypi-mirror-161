

[![](https://codecov.io/gh/nickderobertis/cliconf/branch/main/graph/badge.svg)](https://codecov.io/gh/nickderobertis/cliconf)
[![PyPI](https://img.shields.io/pypi/v/cliconf)](https://pypi.org/project/cliconf/)
![PyPI - License](https://img.shields.io/pypi/l/cliconf)
[![Documentation](https://img.shields.io/badge/documentation-pass-green)](https://nickderobertis.github.io/cliconf/)
![Tests Run on Ubuntu Python Versions](https://img.shields.io/badge/Tests%20Ubuntu%2FPython-3.8%20%7C%203.9%20%7C%203.10-blue)
![Tests Run on Macos Python Versions](https://img.shields.io/badge/Tests%20Macos%2FPython-3.8%20%7C%203.9%20%7C%203.10-blue)
[![Github Repo](https://img.shields.io/badge/repo-github-informational)](https://github.com/nickderobertis/cliconf/)


#  cliconf

## Overview

Framework that lets you write CLIs with Typer that can also be configured via py-app-conf

## Getting Started

Install `cliconf`:

```
pip install cliconf
```

A simple example:

```python
import cliconf

# Do something with cliconf
```

See a
[more in-depth tutorial here.](
https://nickderobertis.github.io/cliconf/tutorial.html
)

## Development Status

This project is currently in early-stage development. There may be
breaking changes often. While the major version is 0, minor version
upgrades will often have breaking changes.

## Developing

First ensure that you have `pipx` installed, if not, install it with `pip install pipx`.

Then clone the repo and run `npm install` and `pipenv sync`. Run `pipenv shell`
to use the virtual environment. Make your changes and then run `nox` to run formatting,
linting, and tests.

Develop documentation by running `nox -s docs` to start up a dev server.

To run tests only, run `nox -s test`. You can pass additional arguments to pytest
by adding them after `--`, e.g. `nox -s test -- -k test_something`.

## Author

Created by Nick DeRobertis. MIT License.

## Links

See the
[documentation here.](
https://nickderobertis.github.io/cliconf/
)
