# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['numalogic',
 'numalogic.models',
 'numalogic.models.autoencoder',
 'numalogic.models.autoencoder.variants',
 'numalogic.models.forecast',
 'numalogic.models.forecast.variants',
 'numalogic.preprocess',
 'numalogic.registry',
 'numalogic.synthetic',
 'numalogic.tests',
 'numalogic.tests.models',
 'numalogic.tests.models.autoencoder',
 'numalogic.tests.models.autoencoder.variants',
 'numalogic.tests.models.forecast',
 'numalogic.tests.preprocess',
 'numalogic.tests.registry',
 'numalogic.tests.synthetic',
 'numalogic.tests.tools',
 'numalogic.tools']

package_data = \
{'': ['*'], 'numalogic.tests': ['resources/data/*']}

install_requires = \
['mlflow-skinny>=1.27.0,<2.0.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'pytz>=2022.1,<2023.0',
 'scikit-learn>=1.0,<2.0',
 'torch>=1.12.0,<2.0.0',
 'torchinfo>=1.6.0,<2.0.0']

setup_kwargs = {
    'name': 'numalogic',
    'version': '0.2.2',
    'description': 'Collection of operational Machine Learning models and tools.',
    'long_description': '# numalogic\n\n[![Build](https://github.com/numaproj/numalogic/actions/workflows/ci.yml/badge.svg)](https://github.com/numaproj/numalogic/actions/workflows/ci.yml)\n[![Coverage](https://github.com/numaproj/numalogic/actions/workflows/coverage.yml/badge.svg?branch=main)](https://github.com/numaproj/numalogic/actions/workflows/coverage.yml)\n[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n\nNuma logic is a collection of operational ML models and tools.\n\n\n## Installation\n\n```shell\npip install numalogic\n```\n\n\n## Develop locally\n\n1. Install Poetry:\n    ```\n    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -\n    ```\n2. To activate virtual env:\n    ```\n    poetry shell\n    ```\n3. To install all dependencies: ( listed on pyproject.toml)\n   ```\n   make setup\n   ```\n4. To install dependencies:\n    ```\n    poetry install\n    ```\n5. To run tests with coverage:\n    ```\n    make test\n    ```\n6. To format code style using black:\n    ```\n    make format\n    ```',
    'author': 'Numalogic Developers',
    'author_email': None,
    'maintainer': 'Avik Basu',
    'maintainer_email': 'avikbasu93@gmail.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
