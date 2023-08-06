# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wmill_pg']

package_data = \
{'': ['*']}

install_requires = \
['psycopg2-binary', 'wmill>=1.5.0,<2.0.0']

setup_kwargs = {
    'name': 'wmill-pg',
    'version': '1.25.0',
    'description': 'An extension client for the wmill client library focused on pg',
    'long_description': '# wmill\n\nThe postgres extension client for the [Windmill](https://windmill.dev) platform.\n\n[windmill-api](https://pypi.org/project/windmill-api/).\n\n## Quickstart\n\n```python\nimport wmill_pg\n\n\ndef main():\n    my_list = query("UPDATE demo SET value = \'value\' RETURNING key, value")\n    for key, value in my_list:\n        ...\n```\n',
    'author': 'Ruben Fiszel',
    'author_email': 'ruben@rubenfiszel.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://windmill.dev',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
