# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rigel', 'rigel.files', 'rigel.models', 'rigel.plugins']

package_data = \
{'': ['*'], 'rigel.files': ['assets/*', 'assets/templates/*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0',
 'PyYAML>=6.0,<7.0',
 'click>=8.0.3,<9.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'rich>=11.2.0,<12.0.0',
 'rigel-local-simulation-plugin>=0.1.0,<0.2.0',
 'rigel-registry-plugin>=0.1.6,<0.2.0',
 'rigelcore>=0.1.19,<0.2.0']

entry_points = \
{'console_scripts': ['rigel = rigel.cli:main']}

setup_kwargs = {
    'name': 'rigel',
    'version': '0.2.22',
    'description': 'Containerize and deploy your ROS application using Docker.',
    'long_description': '# **Rigel**\n',
    'author': 'Pedro Miguel Melo',
    'author_email': 'pedro.m.melo@inesctec.pt',
    'maintainer': 'Pedro Miguel Melo',
    'maintainer_email': 'pedro.m.melo@inesctec.pt',
    'url': 'https://github.com/rigel-ros/rigel',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
