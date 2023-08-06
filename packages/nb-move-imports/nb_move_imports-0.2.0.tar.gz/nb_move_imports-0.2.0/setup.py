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
    'version': '0.2.0',
    'description': 'Move import statements in jupyter notebook to the first cell',
    'long_description': '# nb_move_imports\n\n------------------------------\n\nMove import statements in jupyter notebook to the first cell\n',
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
