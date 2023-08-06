# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wa2rasa']

package_data = \
{'': ['*'], 'wa2rasa': ['my_rasa_dir/*', 'wa_example/My-WA-Skill-dialog.json']}

install_requires = \
['PyYAML>=6.0,<7.0', 'rich>=12.5.1,<13.0.0', 'typer>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['wa2rasa = wa2rasa.cli:app']}

setup_kwargs = {
    'name': 'wa2rasa',
    'version': '0.1.0',
    'description': 'Convert Watson Assistant skill object to rasa nlu.yml file.',
    'long_description': None,
    'author': 'Cloves Paiva',
    'author_email': 'clovesgtx@gmail.com',
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
