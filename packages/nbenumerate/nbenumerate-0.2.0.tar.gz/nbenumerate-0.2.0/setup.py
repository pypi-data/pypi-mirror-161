# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nbenumerate']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.2', 'nbformat>=5.4.0,<6.0.0']

entry_points = \
{'console_scripts': ['jupyter-nbenumerate = nbenumerate.main:main',
                     'nbenumerate = nbenumerate.main:main']}

setup_kwargs = {
    'name': 'nbenumerate',
    'version': '0.2.0',
    'description': 'Automatically enumerate the markdown titles in jupyter notebooks',
    'long_description': '# nbenumerate\n\nAutomatically enumerate the markdown titles in jupyter notebooks.\n\n![Screenshot](./Screenshot.png)\n\n## Installing nbenumerate\n\nInstall nbenumerate with pip:\n\n```console\npip install nbenumerate\n```\n\n## Using nbenumerate\n\nTo run on one or more notebooks:\n\n```console\nnbenumerate path/to/notebook.ipynb\n```\n\n## Precommit Hook\n\nAdd this section to your `pre-commit-config.yaml` so that the `nbenumerate` script is executed before each commit with pre-commit.\n\n```yaml\n- repo: https://github.com/AnH0ang/nbenumerate\n  rev: 0.2.0\n  hooks:\n    - id: nbenumerate\n      name: nbenumerate\n```\n',
    'author': 'An Hoang',
    'author_email': 'anhoang31415@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.9,<4',
}


setup(**setup_kwargs)
