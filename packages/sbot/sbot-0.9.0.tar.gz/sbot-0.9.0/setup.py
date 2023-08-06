# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sbot', 'sbot.vision', 'sbot.vision.calibrations']

package_data = \
{'': ['*']}

install_requires = \
['j5-zoloto>=0.1.0,<0.2.0', 'j5>=0.13.0,<0.14.0']

setup_kwargs = {
    'name': 'sbot',
    'version': '0.9.0',
    'description': 'SourceBots API',
    'long_description': "# sbot\n\n[![CircleCI](https://circleci.com/gh/sourcebots/sbot.svg?style=svg)](https://circleci.com/gh/sourcebots/sbot)\n[![PyPI version](https://badge.fury.io/py/sbot.svg)](https://badge.fury.io/py/sbot)\n[![Documentation Status](https://readthedocs.org/projects/pip/badge/?version=stable)](http://pip.pypa.io/en/stable/?badge=stable)\n[![MIT license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)](https://opensource.org/licenses/MIT)\n![Bees](https://img.shields.io/badge/bees-110%25-yellow.svg)\n\n`sbot` - SourceBots Robot API - Powered by j5\n\nThis is the API for SourceBots, based on the [j5](https://github.com/j5api/j5)\nlibrary for writing Robotics APIs. It will first be deployed at Smallpeice 2019.\n\nMuch like it's predecessor, [robot-api](https://github.com/sourcebots/robot-api), `sbot` supports\nmultiple backends, although should be more reliable as there is no `UNIX-AF` socket layer.\n\n## Installation\n\nInstall: `pip install sbot`\n\nInstall with vision support: `pip install sbot[vision]`\n\n## Usage\n\n```python\n\nfrom sbot import Robot\n\nr = Robot()\n\n```\n\nOr alternatively:\n\n```python\n\nfrom sbot import Robot\n\nr = Robot(wait_start=False)\n\n# Setup in here\n\nr.wait_start()\n\n```\n\n## Adding camera calibrations\n\nYou will need to print off a [chAruco marker grid](https://docs.opencv.org/4.5.3/charuco_board.png).\n\n`opencv_interactive-calibration -t=charuco -sz=GRID_SIZE`\n\nReplace GRID_SIZE with the length of one of the larger squares (in mm) from the printed marker grid.\n\nUse `-ci=1` for specifying camera index if multiple cameras are connected.\n\nPoint the camera at the marker grid. Until DF is at or below 30 then press S to save.\nThis will output a `cameraParameters.xml` file. Place this file in `sbot/vision/calibrations` named after the camera model.\n\nYou will need to edit the calibration file used in `sbot/vision/backend.py`.\n",
    'author': 'SourceBots',
    'author_email': 'hello@sourcebots.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://sourcebots.co.uk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
