# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['capylang']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.2,<2.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'capylang',
    'version': '0.10.8',
    'description': "Python's little programming language.",
    'long_description': '# Capylang\n### Capylang is a pretty simple language.\n### Here is an example of using Capylang.\n```python\nfrom capylang import capy\ncapy.help() # Prints the functions down\ncapy.log("Hello, World!") # Prints Hello, World!\n```\n### That\'s pretty much it for a basic tutorial of Capylang.',
    'author': 'Kia Kazemi',
    'author_email': 'kia@anistick.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0',
}


setup(**setup_kwargs)
