# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sigma', 'sigma.backends.opensearch', 'sigma.pipelines.opensearch']

package_data = \
{'': ['*']}

install_requires = \
['pysigma-backend-elasticsearch>=0.1.0,<0.2.0', 'pysigma>=0.7.1,<0.8.0']

setup_kwargs = {
    'name': 'pysigma-backend-opensearch',
    'version': '0.1.2',
    'description': 'pySigma OpenSearch backend',
    'long_description': None,
    'author': 'Hendrik Baecker',
    'author_email': 'hendrik.baecker@dcso.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SigmaHQ/pySigma-backend-opensearch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
