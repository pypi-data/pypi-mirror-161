# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openai_helper', 'openai_helper.bp', 'openai_helper.dmo', 'openai_helper.svc']

package_data = \
{'': ['*']}

install_requires = \
['baseblock==0.1.4', 'openai>=0.20.0,<0.21.0']

setup_kwargs = {
    'name': 'openai-helper',
    'version': '0.1.1',
    'description': 'OpenAI Helper for Easy I/O',
    'long_description': None,
    'author': 'Craig Trim',
    'author_email': 'craig@bast.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '==3.8.5',
}


setup(**setup_kwargs)
