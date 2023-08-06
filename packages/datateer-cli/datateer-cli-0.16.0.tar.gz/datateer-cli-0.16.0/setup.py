# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datateer_cli',
 'datateer_cli.commands.config',
 'datateer_cli.commands.docs',
 'datateer_cli.commands.echo',
 'datateer_cli.commands.infra',
 'datateer_cli.commands.pipeline',
 'datateer_cli.orchestration']

package_data = \
{'': ['*'],
 'datateer_cli': ['ssh/*'],
 'datateer_cli.commands.pipeline': ['flow/*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0',
 'boto3>=1.20.37,<2.0.0',
 'click>=7.0',
 'erd-python>=0.6.2,<0.7.0',
 'pathspec>=0.9.0,<0.10.0']

entry_points = \
{'console_scripts': ['datateer = datateer_cli.cli:main']}

setup_kwargs = {
    'name': 'datateer-cli',
    'version': '0.16.0',
    'description': 'Datateer CLI to support devops and infrastructure',
    'long_description': None,
    'author': 'Datateer',
    'author_email': 'dev@datateer.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
