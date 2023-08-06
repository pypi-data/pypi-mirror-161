# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['telegrinder',
 'telegrinder.api',
 'telegrinder.bot',
 'telegrinder.bot.cute_types',
 'telegrinder.bot.dispatch',
 'telegrinder.bot.dispatch.handler',
 'telegrinder.bot.dispatch.middleware',
 'telegrinder.bot.dispatch.view',
 'telegrinder.bot.polling',
 'telegrinder.bot.scenario',
 'telegrinder.http_',
 'telegrinder.tools',
 'telegrinder.tools.formatting',
 'telegrinder.tools.kb_set',
 'telegrinder.types']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'aiohttp>=3.8.1,<4.0.0',
 'choicelib>=0.1.5,<0.2.0',
 'envparse>=0.2.0,<0.3.0',
 'pydantic>=1.9.0,<2.0.0',
 'vbml>=1.1.post1,<2.0']

setup_kwargs = {
    'name': 'telegrinder',
    'version': '0.1.dev5',
    'description': 'Grinding telegram events – customizable tool to build telegram bots',
    'long_description': None,
    'author': 'timoniq',
    'author_email': 'tesseradecades@mail.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
