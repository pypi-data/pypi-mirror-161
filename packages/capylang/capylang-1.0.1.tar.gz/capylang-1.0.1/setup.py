# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['capylang', 'capylang.cjson', 'capylang.http']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.22.2,<2.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'capylang',
    'version': '1.0.1',
    'description': "Python's little programming language.",
    'long_description': "# Capylang\n### Capylang is a pretty simple language.\n### Here is an example of using Capylang.\n```python\nfrom capylang import capy\na = 5\nb = 2\ncapy.help() # Prints the functions down\ncapy.log(str(capy.add(a,b))) # Prints 7 (also uses the add function)\ncapy.log(str(capy.sub(a,b))) # Prints 3 (also uses the subtract function)\ncapy.log(str(capy.multi(a,b))) # Prints 10 (also uses the multiply function)\ncapy.log(str(capy.div(a,b))) # Prints 2.5 (also uses the divide function)\ncapy.log(str(capy.hyp(a,b))) # Try this yourself for more info, check capy.help()\ncapy.log(str(capy.opp(a,b))) # Try this yourself for more info, check capy.help()\ncapy.log(str(capy.adj(a,b))) # Try this yourself for more info, check capy.help()\ncapy.auto_update(True) # Turns on auto updating. Auto updating is set to False by default.\n```\n### That's pretty much it for a basic tutorial of Capylang.",
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
