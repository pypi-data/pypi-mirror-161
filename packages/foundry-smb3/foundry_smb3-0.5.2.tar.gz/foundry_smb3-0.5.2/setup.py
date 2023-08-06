# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['foundry',
 'foundry.core',
 'foundry.core.blocks',
 'foundry.core.drawable',
 'foundry.core.file',
 'foundry.core.graphics_page',
 'foundry.core.graphics_set',
 'foundry.core.painter',
 'foundry.core.palette',
 'foundry.core.player_animations',
 'foundry.core.sprites',
 'foundry.core.tiles',
 'foundry.core.warnings',
 'foundry.game',
 'foundry.game.gfx',
 'foundry.game.gfx.drawable',
 'foundry.game.gfx.objects',
 'foundry.game.level',
 'foundry.gui',
 'foundry.smb3parse',
 'foundry.smb3parse.levels',
 'foundry.smb3parse.objects',
 'foundry.smb3parse.util']

package_data = \
{'': ['*'], 'foundry': ['data/*', 'data/icons/*']}

install_requires = \
['PySide6>=6.3.0,<7.0.0',
 'attrs>=21.2.0,<22.0.0',
 'autodoc-pydantic>=1.6.1,<2.0.0',
 'black>=22.3.0,<23.0.0',
 'pretty-errors>=1.2.24,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pyupgrade>=2.37.3,<3.0.0',
 'qt-material>=2.8.13,<3.0.0',
 'single-source>=0.2.0,<0.3.0']

entry_points = \
{'console_scripts': ['foundry = foundry.main:start']}

setup_kwargs = {
    'name': 'foundry-smb3',
    'version': '0.5.2',
    'description': 'The future of SMB3',
    'long_description': '# Foundry\n\n<p align="center">\n<a href="https://github.com/TheJoeSmo/Foundry/actions"><img alt="Actions Status" src="https://github.com/TheJoeSmo/Foundry/actions/workflows/tests.yml/badge.svg"></a>\n<a href="https://github.com/TheJoeSmo/Foundry/actions"><img alt="Actions Status" src="https://github.com/TheJoeSmo/Foundry/actions/workflows/github_pages.yml/badge.svg"></a>\n<a href="https://github.com/TheJoeSmo/Foundry/block/main/LICENSE.md"><img alt="License GPL3" src="https://img.shields.io/badge/License-GPLv3-blue.svg"></a>\n<a href="https://pypi.org/project/foundry-smb3/"><img alt="PyPI" src="https://img.shields.io/pypi/v/foundry-smb3"></a>\n<a href="https://pepy.tech/project/black"><img alt="Downloads" src="https://pepy.tech/badge/foundry-smb3"></a>\n<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n</p>\n\nPurpose\n-------\nFoundry is the all-in-one editor for modifying copies of the North American release of [SMB3](https://en.wikipedia.org/wiki/Super_Mario_Bros._3).  We seek to streamline the game development processes to ensure that the nostalgic memories of [Power Glove](https://en.wikipedia.org/wiki/Power_Glove), [Nintendo Power](https://en.wikipedia.org/wiki/Nintendo_Power), and goomba stomping can be accessed and modified by all.  We want to put the power into our favorite game and you the super player!\n\n\nInstallation\n------------\nTo install and use Foundry, there are three options:\n\n1. [Download Foundry Executable](https://github.com/TheJoeSmo/Foundry/releases)\n    \n    This is the every-person method.  Every minor and major release will prepackage the editor into an executable to run painlessly on your native machine.  To get started, go to [Releases](https://github.com/TheJoeSmo/Foundry/releases) and download the executable specific to your operating system.\n\n2. [Download Foundry from PyPi](https://pypi.org/project/foundry-smb3/)\n    \n    This is the method recommended if you wish to run the project natively with Python.  This may required if you use a 32 bit machine or an obscure operating system.  It is also required if you wish to use Foundry in some combination with other Python packages.  With [Python](https://www.python.org/downloads/) installed, write `pip install foundry-smb3` into your console and run `foundry` or run `foundry.main.start` from inside Python.\n\n3. [Download Foundry from Github](https://github.com/TheJoeSmo/Foundry.git)\n\n    This is the developer method.  This will provide you easy access to the entire repository.  In addition to [Python](https://www.python.org/downloads/) you will need [Poetry](https://python-poetry.org/docs/) installed.  Once installed run the following commands into your terminal:\n\n    ```\n    $ git clone git@github.com:TheJoeSmo/Foundry.git\n    $ cd Foundry\n    $ poetry install\n    ```\n\nDocumentation\n-------------\n\nAll documentation of the editor can be found at [Foundry Documentation](https://thejoesmo.github.io/Foundry/).\n\n\nCall for Contributions\n----------------------\nFoundry is a community driven initiative that relies on your help and expertise.\n\nSmall improvements or fixes are critical to this repository\'s success.  Issues labeled `good first issue` are a great place to start.  For larger contributions WIP.\n\nYou do not need to be literate with programming to aid Foundry on its journey.  We also need help with:\n- Developing tutorials\n- Creating graphics for our brand and promotional material\n- Translation\n- Outreach and onboarding new contributors\n- Reviewing issues and suggestions\n\nIf you are undecided on where to start, we encourage you to reach out.  You can ask on our Discord or privately through email.\n\nIf you are new to open source projects and want to be caught up to speed, we recommend [this guide](https://opensource.guide/how-to-contribute/)\n\nImportant Links\n---------------\n- [Website](https://thejoesmo.github.io/Foundry/)\n- [Discord](https://discord.gg/pm87gm7)\n- [Documentation](https://thejoesmo.github.io/Foundry/)\n- [Manual](https://github.com/TheJoeSmo/Foundry/blob/master/MANUAL.md)\n- [Source Code](https://github.com/TheJoeSmo/Foundry)\n- [Bug Reporting](https://github.com/TheJoeSmo/Foundry/issues)\n',
    'author': 'TheJoeSmo',
    'author_email': 'joesmo.joesmo12@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10.0,<3.11',
}


setup(**setup_kwargs)
