# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['robotmpcs', 'robotmpcs.models', 'robotmpcs.planner']

package_data = \
{'': ['*']}

install_requires = \
['casadi>=3.5.4,<4.0.0,!=3.5.5.post1,!=3.5.5.post2',
 'forwardkinematics>=1.0.3,<2.0.0',
 'numpy>=1.15.3,<2.0.0',
 'pyaml>=21.10.1,<22.0.0',
 'requests>=2.27.1,<3.0.0',
 'scipy>=1.5.0,<2.0.0']

extras_require = \
{'agents': ['motion-planning-scenes>=0.1,<0.2',
            'planarenvs>=1.0.3,<2.0.0',
            'urdfenvs>=0.2.2,<0.3.0']}

setup_kwargs = {
    'name': 'robotmpcs',
    'version': '0.1.6',
    'description': 'MPC generation for robots using ForcesPro.',
    'long_description': None,
    'author': 'Max Spahn',
    'author_email': 'm.spahn@tudelft.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.5,<3.10',
}


setup(**setup_kwargs)
