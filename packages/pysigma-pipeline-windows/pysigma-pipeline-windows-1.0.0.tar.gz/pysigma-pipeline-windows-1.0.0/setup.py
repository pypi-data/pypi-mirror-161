# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sigma', 'sigma.pipelines.windows']

package_data = \
{'': ['*']}

install_requires = \
['pysigma>=0.7.2,<0.8.0']

setup_kwargs = {
    'name': 'pysigma-pipeline-windows',
    'version': '1.0.0',
    'description': 'pySigma Windows processing pipelines',
    'long_description': None,
    'author': 'frack113',
    'author_email': 'frack113@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SigmaHQ/pySigma-pipeline-windows',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
