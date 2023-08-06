# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dictum']

package_data = \
{'': ['*']}

install_requires = \
['dictum-core>=0.1,<0.2']

extras_require = \
{'postgres': ['dictum-backend-postgres>=0.1,<0.2'],
 'vertica': ['dictum-backend-vertica>=0.1,<0.2']}

setup_kwargs = {
    'name': 'dictum',
    'version': '0.1.4',
    'description': 'Describe business metrics with YAML, query and visualize in Jupyter with zero SQL',
    'long_description': None,
    'author': 'Mikhail Akimov',
    'author_email': 'rovinj.akimov@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
