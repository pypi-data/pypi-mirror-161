# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scythe_cli',
 'scythe_cli.application',
 'scythe_cli.clock',
 'scythe_cli.harvest_api']

package_data = \
{'': ['*']}

install_requires = \
['arc-cli==7.0.0',
 'diskcache>=5.4.0,<6.0.0',
 'oyaml>=1.0,<2.0',
 'pydantic>=1.9.0,<2.0.0',
 'requests>=2.25.1,<3.0.0',
 'rich>=12.0.0,<13.0.0',
 'xdg>=5.1.1,<6.0.0']

entry_points = \
{'console_scripts': ['scythe = scythe_cli.application:cli']}

setup_kwargs = {
    'name': 'scythe-cli',
    'version': '0.14.0',
    'description': 'A Harvest is always better with a good tool',
    'long_description': '',
    'author': 'Sean Collings',
    'author_email': 'seanrcollings@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/seanrcollings/scythe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
