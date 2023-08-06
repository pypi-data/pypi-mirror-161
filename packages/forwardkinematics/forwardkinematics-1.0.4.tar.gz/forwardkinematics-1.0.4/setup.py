# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['forwardkinematics',
 'forwardkinematics.fksCommon',
 'forwardkinematics.planarFks',
 'forwardkinematics.urdfFks',
 'forwardkinematics.urdfFks.casadiConversion',
 'forwardkinematics.urdfFks.casadiConversion.geometry']

package_data = \
{'': ['*'], 'forwardkinematics.urdfFks': ['urdf/*']}

install_requires = \
['casadi>=3.5.4,<4.0.0,!=3.5.5.post1,!=3.5.5.post2',
 'numpy>=1.15.3,<2.0.0',
 'urdf_parser_py>=0.0.3']

setup_kwargs = {
    'name': 'forwardkinematics',
    'version': '1.0.4',
    'description': '"Light-weight implementation of forward kinematics using casadi."',
    'long_description': '# Installation\n\nThis package provides a forward kinematics for simple robots as symbolic functions using\ncasadi. This allows the usage in model predictive control schemes and other trajectory\noptimization methods.\n\n```bash\npip3 install forwardkinematics\n```\n\n## Install in editable mode\n\nIf you want to install as an editable without the usage of an virtual environment, you\nmust create a setup.py first.\nThis can be done using poetry2setup (`pip install poetry2setup`)\nThen you can run \n```bash\npoetry2setup > setup.py\nmv pyproject.toml pyproject.toml_BACKUP\npip3 install -e .\n```\n',
    'author': 'Max Spahn',
    'author_email': 'm.spahn@tudelft.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/maxspahn/forwardKinematics.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<3.10',
}


setup(**setup_kwargs)
