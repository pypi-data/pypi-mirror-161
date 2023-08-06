# nb_move_imports

------------------------------
[![PyPI version](https://badge.fury.io/py/nb_move_imports.svg)](https://badge.fury.io/py/nb_move_imports)
[![Python version](https://img.shields.io/badge/python-≥3.8-blue.svg)](https://pypi.org/project/kedro/)
[![Release Pipeline](https://github.com/AnH0ang/nb_move_imports/actions/workflows/release.yml/badge.svg)](https://github.com/AnH0ang/nb_move_imports/actions/workflows/release.yml)
[![Test](https://github.com/AnH0ang/nb_move_imports/actions/workflows/test.yml/badge.svg)](https://github.com/AnH0ang/nb_move_imports/actions/workflows/test.yml)
[![Code Quality](https://github.com/AnH0ang/nb_move_imports/actions/workflows/code_quality.yml/badge.svg)](https://github.com/AnH0ang/nb_move_imports/actions/workflows/code_quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/STATWORX/statworx-theme/blob/master/LICENSE)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)

Move import statements in jupyter notebook to the first cell

## Use nb_move_imports

To run the script on a specific jupyter notebook run:

```console
nb_move_imports path/to/notebook.ipynb
```

## Skip processing of cells

In order to skip a cell you have to tag it with the `IGNORE_MV_IMPORTS` tag.

## Precommit Hook

Add this section to your `pre-commit-config.yaml` so that the nb_move_imports script is executed before each commit with pre-commit.

```yaml
- repo: https://github.com/AnH0ang/nb_move_imports
  rev: 0.4.0
  hooks:
    - id: nb_move_imports
      name: nb_move_imports
```
