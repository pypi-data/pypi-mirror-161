# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['masterlist', 'altstats']
install_requires = \
['Brotli>=1.0.9,<2.0.0', 'requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'altvmasterlist',
    'version': '2.2.8',
    'description': 'A package to use the alt:V Masterlist api.',
    'long_description': '# alt:V Masterlist for Python\n\nYou can use this Package to interface with the alt:V master list API and with the altstats.net API.\n\n# Install \n\n```pip install altvmasterlist``` or ```pip3 install altvmasterlist```\n\n# Usage\n\n```\nimport masterlist as altv\n...\nor\n...\nimport altstats as altv\n```\n\n# Docs\n\nPlease see the Docs [here](https://nickwasused.github.io/altv-python-masterlist/).',
    'author': 'Nickwasused',
    'author_email': 'contact.nickwasused.fa6c8@simplelogin.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Nickwasused/altv-python-masterlist',
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
