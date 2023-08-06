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
    'version': '0.1.2',
    'description': 'Convert Watson Assistant skill object to rasa nlu.yml file.',
    'long_description': 'Purpose of the Package\n======================\n\nConvert intents and entities defined in the Watson Assistant skill\nobject to rasa nlu.yml file.\n\nGiven how rasa works, there is no way to translate dialog flows defined\nin WA into rasa stories. So this converter don’t intends to take care of\ndialog flows.\n\nInstallation\n============\n\nYou can use pip:\n\n.. code:: bash\n\n   $ pip3 install wa2rasa\n\n*Rasa* and *wa2rasa* use common libraries, to avoid conflicts please\ninstall *wa2rasa* in a separate virtual environment.\n\nUsage\n=====\n\nJust run the following command:\n\n.. code:: bash\n\n   $ wa2rasa convert <path_to_your_wa_object>/ <directory_to_store_rasa_nlu_file>/\n\nHere a gif for you:\n\n.. figure:: https://media.giphy.com/media/zQxXPs9HhNJHZBI1Iy/giphy.gif\n   :alt: how to use the wa2rasa\n\nAuthor\n======\n\n`Cloves Paiva <https://www.linkedin.com/in/cloves-paiva-02b449124/>`__.\n',
    'author': 'Cloves Paiva',
    'author_email': 'clovesgtx@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SClovesgtx/wa2rasa',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
