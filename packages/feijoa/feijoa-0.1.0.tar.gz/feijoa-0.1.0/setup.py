# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['feijoa',
 'feijoa.importance',
 'feijoa.jobs',
 'feijoa.models',
 'feijoa.search',
 'feijoa.search.algorithms',
 'feijoa.storages',
 'feijoa.storages.rdb',
 'feijoa.utils',
 'feijoa.visualization']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.35,<2.0.0',
 'click>=8.1.2',
 'executor>=23.2',
 'mabalgs>=0.6.8,<0.7.0',
 'numba>=0.55.2',
 'numpy>=1.22.3',
 'pandas>=1.4.2',
 'plotly>=5.9.0,<6.0.0',
 'pydantic>=1.9.0',
 'pydeps>=1.10.18',
 'pytest-cov>=3.0.0,<4.0.0',
 'rich>=12.2.0',
 'scikit-optimize>=0.9.0',
 'sklearn>=0.0,<0.1',
 'tinydb>=4.7.0,<5.0.0']

setup_kwargs = {
    'name': 'feijoa',
    'version': '0.1.0',
    'description': "Hyperparameter's optimization framework",
    'long_description': "![PyPI - Python Version](https://img.shields.io/pypi/pyversions/feijoa?style=for-the-badge) ![PyPI](https://img.shields.io/pypi/v/feijoa?style=for-the-badge) ![Codecov](https://img.shields.io/codecov/c/github/qnbhd/feijoa?style=for-the-badge)\n\nFeijoa is a Python framework for hyperparameter's optimization.\n\nThe Feijoa API is very easy to use, effective for optimizing machine learning algorithms and various software. Feijoa contains many different use cases.\n\n## Compatibility\n\nFeijoa works with Linux and OS X. Requires Python 3.8 or later.\n\nFeijoa works with [Jupyter notebooks](https://jupyter.org/) with no additional configuration required.\n\n# Installing\n\nInstall with `pip` or your favourite PyPI package manager.\n\n`python -m pip install feijoa`\n\n## Code example:\n\n```python\nfrom feijoa import create_job, Experiment, SearchSpace, Real\nfrom math import sin\n\n\ndef objective(experiment: Experiment):\n    x = experiment.params.get('x')\n    y = experiment.params.get('y')\n\n    return sin(x * y)\n    \nspace = SearchSpace()\nspace.insert(Real('x', low=0.0, high=2.0))\nspace.insert(Real('y', low=0.0, high=2.0))\n\njob = create_job(search_space=space)\njob.do(objective)\n```\n\n",
    'author': 'Konstantin Templin',
    'author_email': '1qnbhd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/qnbhd/feijoa',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
