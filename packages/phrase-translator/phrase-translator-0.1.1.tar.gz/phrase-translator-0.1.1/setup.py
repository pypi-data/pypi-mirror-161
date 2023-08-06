# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['phrase_translator']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'phrase-translator',
    'version': '0.1.1',
    'description': 'A very simple package to translate single words and phrases between different languages.',
    'long_description': '### Phrase Translator\n\nA very simple package to translate single words and phrases between different languages.\n',
    'author': 'Fabian Richter',
    'author_email': 'me@fr2501.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
