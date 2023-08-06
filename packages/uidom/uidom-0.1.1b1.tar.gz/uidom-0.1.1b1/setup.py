# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uidom',
 'uidom.asgi_plugs',
 'uidom.components',
 'uidom.components.alpinejs',
 'uidom.components.atoms',
 'uidom.dom',
 'uidom.dom.elements',
 'uidom.dom.iconify',
 'uidom.dom.iconify.account',
 'uidom.dom.iconify.brands',
 'uidom.dom.src',
 'uidom.dom.src.tests',
 'uidom.dom.src.utils',
 'uidom.dom.tailwindcss',
 'uidom.dom.tailwindcss.background',
 'uidom.dom.tailwindcss.flexbox',
 'uidom.dom.tailwindcss.gridbox',
 'uidom.dom.tailwindcss.layout',
 'uidom.dom.tailwindcss.sizing',
 'uidom.dom.tailwindcss.spacing',
 'uidom.dom.tailwindcss.typography',
 'uidom.dom.utils',
 'uidom.dom.widgets',
 'uidom.edge_db',
 'uidom.response',
 'uidom.settings',
 'uidom.web_io']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'aiofiles>=0.7.0,<0.8.0',
 'pytailwindcss>=0.1.4,<0.2.0',
 'python-multipart>=0.0.5,<0.0.6',
 'starlette==0.19.1',
 'valio>=0.1.0-beta.5,<0.2.0']

setup_kwargs = {
    'name': 'uidom',
    'version': '0.1.1b1',
    'description': 'HTML library',
    'long_description': None,
    'author': 'bitplorer',
    'author_email': 'bitplorer@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
