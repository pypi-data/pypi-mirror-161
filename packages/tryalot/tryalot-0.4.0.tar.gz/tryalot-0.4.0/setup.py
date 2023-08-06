# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tryalot']

package_data = \
{'': ['*']}

install_requires = \
['graphviz>=0.19.1,<0.20.0', 'zstandard>=0.16.0,<0.17.0']

setup_kwargs = {
    'name': 'tryalot',
    'version': '0.4.0',
    'description': 'Try a lot without worrying about the hassle.',
    'long_description': '# tryalot\n\nTry a lot without worrying about the hassle.\n\nThis is a fromework that helps you do a bunch of computational experiments.\n',
    'author': 'Yuta Taniguchi',
    'author_email': 'yuta.taniguchi.y.t@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yuttie/tryalot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
