# nbenumerate

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
  rev: 0.2.0
  hooks:
    - id: nbenumerate
      name: nbenumerate
```
