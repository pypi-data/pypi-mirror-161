# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cbinterface', 'cbinterface.psc', 'cbinterface.response', 'cbinterface.tools']

package_data = \
{'': ['*'], 'cbinterface': ['playbook_configs/*', 'templates/*']}

install_requires = \
['argcomplete>=2.0.0,<3.0.0', 'cbapi>=1.7.3,<2.0.0', 'coloredlogs>=15.0,<16.0']

setup_kwargs = {
    'name': 'cbinterface',
    'version': '2.3.34',
    'description': 'command line tool for interfacing with multiple carbonblack environments to perform analysis and live response functions',
    'long_description': "# cbinterface\n\n`cbinterface` is a command line tool and library for interfacing with one or more Carbon Black environments. \n\nAs of now, `cbinterface` primarily supports Carbon Black PSC EDR (Threathunter) and Carbon Black Response. However, a lot of functionality should also work with other CBC products, like Enterprise Standard. If you're using Enterprise Standard and something doesn't work, open an issue and I can likely swap out an underlying object and have it working quickly.\n\n# Install & Setup\n\n## Install Via pip\n\n```bash\npip install cbinterface\n```\n\n## Install Direct from Github\n\n```\npip install git+https://github.com/ace-ecosystem/cbinterface2\n```\n\n## Setup & Configure\n\n[Look here](https://github.com/ace-ecosystem/cbinterface2/wiki/Configuration) for help setting up and configuring `cbinterface`\t to work with your Carbon Black enviroments and according to your preferences.\n\n\n# The Wiki\n\nCheck out the [Wiki Page](https://github.com/ace-ecosystem/cbinterface2/wiki) for detailed documentation and help.\n\nThat said, if you don't find what you need, have a question about anything, or encounter an issue, open an issue here on Github and I'll help or fix it. If there is interest, I'll create more documentation around any subject.\n\n",
    'author': 'Sean McFeely',
    'author_email': 'mcfeelynaes@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ace-ecosystem/cbinterface2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
