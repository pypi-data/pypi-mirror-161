# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['magma', 'magma_ff']

package_data = \
{'': ['*']}

install_requires = \
['dcicutils>=4.0.0,<5.0.0', 'tibanna-ff>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'magma-suite',
    'version': '1.0.1',
    'description': 'Collection of tools to manage meta-workflows automation.',
    'long_description': '# magma\n\n[*Documentation*](https://magma-suite.readthedocs.io/en/latest/ "magma documentation")\n',
    'author': 'Michele Berselli',
    'author_email': 'berselli.michele@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dbmi-bgm/magma',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.9',
}


setup(**setup_kwargs)
