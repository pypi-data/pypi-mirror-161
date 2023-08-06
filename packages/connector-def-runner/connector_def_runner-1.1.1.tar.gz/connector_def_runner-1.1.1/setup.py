# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['connector_definition_runner']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'chevron>=0.14.0,<1.0.0', 'requests==2.28.0']

setup_kwargs = {
    'name': 'connector-def-runner',
    'version': '1.1.1',
    'description': 'Run connectors by schema definitions',
    'long_description': '# TODO',
    'author': 'Swimlane',
    'author_email': 'integrations@swimlane.com',
    'maintainer': 'Swimlane',
    'maintainer_email': None,
    'url': 'https://github.com/swimlane/connector-definition-runner',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
