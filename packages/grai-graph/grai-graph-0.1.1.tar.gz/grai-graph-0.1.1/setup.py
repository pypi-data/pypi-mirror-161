# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['grai_graph']

package_data = \
{'': ['*']}

install_requires = \
['grai-client>=0.1.3,<0.2.0',
 'networkx>=2.8.5,<3.0.0',
 'pydantic>=1.9.1,<2.0.0']

extras_require = \
{'vis': ['matplotlib>=3.5.2,<4.0.0', 'pydot>=1.4.2,<2.0.0']}

setup_kwargs = {
    'name': 'grai-graph',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Ian Eaves',
    'author_email': 'ian@grai.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
