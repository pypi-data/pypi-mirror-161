# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['corasa', 'corasa.actions', 'corasa.api', 'corasa.components']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp==3.8.1',
 'fastapi>=0.79.0,<0.80.0',
 'pydantic==1.9.1',
 'python-dateutil==2.8.1',
 'python-multipart==0.0.5',
 'requests>=2.24.0,<3.0.0',
 'starlette==0.19.1',
 'twilio==6.50.1',
 'uvicorn==0.18.2']

setup_kwargs = {
    'name': 'corasa',
    'version': '0.1.14',
    'description': 'Components for running a RASA project exported from Colang.',
    'long_description': None,
    'author': 'Razvan Dinu',
    'author_email': 'drazvan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
