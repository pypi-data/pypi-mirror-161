# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['api_correios', 'api_correios.schema', 'api_correios.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.4.0,<3.0.0', 'pydantic>=1.9.1,<2.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'api-correios',
    'version': '0.2.5',
    'description': 'Módulo de integração com a nova versão REST API dos Correios',
    'long_description': None,
    'author': 'Bruno Souza',
    'author_email': 'bruno.souza@zaxapp.com.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.12,<4.0.0',
}


setup(**setup_kwargs)
