# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tailscale_agent']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'tailscale-agent',
    'version': '0.2.0',
    'description': 'Python Bindings for the TailScal API',
    'long_description': '# tailscale-python-client\nPython bindings for the TailScale API\n\nThis is still very much a work in progress and not all API methods are represented\n',
    'author': 'Kevin Bringard',
    'author_email': 'kevin.bringard@phreesia.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kevinbringard/tailscale-python-client/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
