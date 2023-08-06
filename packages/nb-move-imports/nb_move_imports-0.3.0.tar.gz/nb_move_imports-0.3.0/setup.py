# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nb_move_imports']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0', 'isort>=5.10.1,<6.0.0', 'nbformat>=5.4.0,<6.0.0']

entry_points = \
{'console_scripts': ['jupyter-nbmoveimports = nb_move_imports.main:main',
                     'nb_move_imports = nb_move_imports.main:main']}

setup_kwargs = {
    'name': 'nb-move-imports',
    'version': '0.3.0',
    'description': 'Move import statements in jupyter notebook to the first cell',
    'long_description': '# nb_move_imports\n\n------------------------------\n[![PyPI version](https://badge.fury.io/py/nb_move_imports.svg)](https://badge.fury.io/py/nb_move_imports)\n[![Python version](https://img.shields.io/badge/python-≥3.8-blue.svg)](https://pypi.org/project/kedro/)\n[![Release Pipeline](https://github.com/AnH0ang/nb_move_imports/actions/workflows/release.yml/badge.svg)](https://github.com/AnH0ang/nb_move_imports/actions/workflows/release.yml)\n[![Test](https://github.com/AnH0ang/nb_move_imports/actions/workflows/test.yml/badge.svg)](https://github.com/AnH0ang/nb_move_imports/actions/workflows/test.yml)\n[![Code Quality](https://github.com/AnH0ang/nb_move_imports/actions/workflows/code_quality.yml/badge.svg)](https://github.com/AnH0ang/nb_move_imports/actions/workflows/code_quality.yml)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/STATWORX/statworx-theme/blob/master/LICENSE)\n![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)\n\nMove import statements in jupyter notebook to the first cell\n\n## Use nb_move_imports\n\nTo run the script on a specific jupyter notebook run:\n\n```console\nnb_move_imports path/to/notebook.ipynb\n```\n\n## Skip processing of cells\n\nIn order to skip a cell you have to tag it with the `IGNORE_MV_IMPORTS` tag.\n\n## Precommit Hook\n\nAdd this section to your `pre-commit-config.yaml` so that the nb_move_imports script is executed before each commit with pre-commit.\n\n```yaml\n- repo: https://github.com/pre-commit/pre-commit-hooks\n  rev: 0.2.0\n  hooks:\n    - id: nb_move_imports\n      name: nb_move_imports\n```\n',
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
    'python_requires': '>=3.8.9,<4.0.0',
}


setup(**setup_kwargs)
