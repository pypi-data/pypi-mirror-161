# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wifi']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'wifi-ap-force',
    'version': '1.0.3',
    'description': 'Command line tool and library wrappers around iwlist and /etc/network/interfaces.',
    'long_description': '# wifi-ap-force\n\nWifi provides a command line wrapper for iwlist and /etc/network/interfaces\nthat makes it easier to connect the WiFi networks from the command line. The\nwifi command is also implemented as a library that can be used from Python.\n\nThis fork takes care of the "ap-force" option when running iw.\nAlso, the binary is not /sbin/iwlist anymore, but iw directly (/usr/sbin/iw),\ntherefore the command is a bit different.\n\nIt\'s a drop-in replacement of the original package.\n\n```bash\npip install wifi-ap-force\nwifi --help\n```\n\nThe original documentation for wifi lives at https://wifi.readthedocs.org/en/latest/.\n',
    'author': 'Rocky Meza',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
