# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['blade']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pyblade',
    'version': '0.0.1',
    'description': 'A dependency injection library.',
    'long_description': '# pydirk\nA Python dependency injection library.\n',
    'author': 'Michael Dimchuk',
    'author_email': 'michaeldimchuk@gmail.com',
    'maintainer': 'Michael Dimchuk',
    'maintainer_email': 'michaeldimchuk@gmail.com',
    'url': 'https://github.com/michaeldimchuk/pyblade',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
