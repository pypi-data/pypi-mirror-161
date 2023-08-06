# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['MotionPlanningEnv', 'MotionPlanningGoal', 'MotionPlanningSceneHelpers']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'casadi>=3.5.4,<4.0.0,!=3.5.5.post1,!=3.5.5.post2',
 'geomdl>=5.3.1,<6.0.0',
 'numpy>=1.19.0,<2.0.0',
 'omegaconf>=2.2.2,<3.0.0',
 'pyquaternion>=0.9.9,<0.10.0',
 'pytest>=6.2.5,<7.0.0']

extras_require = \
{':python_version < "3.7"': ['dataclasses>=0.8,<0.9']}

setup_kwargs = {
    'name': 'motion-planning-scenes',
    'version': '0.1.22',
    'description': 'Generic motion planning scenes, including goals and obstacles.',
    'long_description': None,
    'author': 'Max',
    'author_email': 'm.spahn@tudelft.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<3.10',
}


setup(**setup_kwargs)
