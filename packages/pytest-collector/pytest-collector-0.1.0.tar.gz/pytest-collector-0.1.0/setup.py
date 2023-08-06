# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytest_collector']

package_data = \
{'': ['*']}

install_requires = \
['pytest>=7.0,<8.0']

setup_kwargs = {
    'name': 'pytest-collector',
    'version': '0.1.0',
    'description': 'Python package for collecting pytest.',
    'long_description': '# pytest-collector\nPython package for collecting pytest tests.\n\n## Usage\n\n`pip install pytest-collector`\n\n```\nimport pytest_collector\n\n# NOTE: this call will import the tests to the current process.\ntest_modules = pytest_collector.collect("path/to/tests/directory")\n```',
    'author': 'michael tadnir',
    'author_email': 'tadnir50@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tadnir/pytest-collector',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
