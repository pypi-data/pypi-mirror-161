# nbenumerate

[![PyPI version](https://badge.fury.io/py/nbenumerate.svg)](https://badge.fury.io/py/nbenumerate)
[![Python version](https://img.shields.io/badge/python-≥3.8-blue.svg)](https://pypi.org/project/kedro/)
[![Code Quality](https://github.com/AnH0ang/nbenumerate/actions/workflows/code_quality.yml/badge.svg)](https://github.com/AnH0ang/nbenumerate/actions/workflows/code_quality.yml)
[![Test](https://github.com/AnH0ang/nbenumerate/actions/workflows/test.yml/badge.svg)](https://github.com/AnH0ang/nbenumerate/actions/workflows/test.yml)
[![Release Pipeline](https://github.com/AnH0ang/nbenumerate/actions/workflows/release.yml/badge.svg)](https://github.com/AnH0ang/nbenumerate/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/STATWORX/statworx-theme/blob/master/LICENSE)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)

Automatically enumerate the markdown titles in jupyter notebooks.

![Screenshot](./Screenshot.png)

## Installing nbenumerate

Install nbenumerate with pip:

```console
pip install nbenumerate
```

## Using nbenumerate

To run on one or more notebooks:

```console
nbenumerate path/to/notebook.ipynb
```

## Precommit Hook

Add this section to your `pre-commit-config.yaml` so that the `nbenumerate` script is executed before each commit with pre-commit.

```yaml
- repo: https://github.com/AnH0ang/nbenumerate
  rev: 0.2.1
  hooks:
    - id: nbenumerate
      name: nbenumerate
```
