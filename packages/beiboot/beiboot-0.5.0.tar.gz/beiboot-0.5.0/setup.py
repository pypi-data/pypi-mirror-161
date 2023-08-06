# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['beiboot']

package_data = \
{'': ['*']}

install_requires = \
['docker>=5.0.3,<6.0.0', 'kubernetes>=23.3.0,<24.0.0']

entry_points = \
{'console_scripts': ['create = testing.exec:create_a_cluster',
                     'remove = testing.exec:remove_a_cluster']}

setup_kwargs = {
    'name': 'beiboot',
    'version': '0.5.0',
    'description': 'Getdeck Beiboot client project.',
    'long_description': '<p align="center">\n  <img src="https://github.com/Getdeck/beiboot/raw/main/docs/static/img/logo.png" alt="Gefyra Logo"/>\n</p>\n\n# Getdeck Beiboot\n_Getdeck Beiboot_ (or just Beiboot for brevity) is a Kubernetes-in-Kubernetes solution. It was born from the idea to \nprovide Getdeck users a simple yet flexible solution to spin up **hybrid cloud development** infrastructure. This is \nuseful for Kubernetes development workloads which grew too large to run on a development machine (or with pony workloads \non MacOS and Windows machines). \n\n# Beiboot Client\nThe Beiboot client is a Python API to manage Beiboot clusters. It can set up and tear down Kubernetes instances\nas well as establish connections.',
    'author': 'Michael Schilonka',
    'author_email': 'michael@blueshoe.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://getdeck.dev',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
