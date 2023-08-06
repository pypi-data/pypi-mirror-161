# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['limeutils', 'limeutils.redis']

package_data = \
{'': ['*'],
 'limeutils': ['.idea/.gitignore',
               '.idea/.gitignore',
               '.idea/.gitignore',
               '.idea/.gitignore',
               '.idea/.gitignore',
               '.idea/inspectionProfiles/*',
               '.idea/limeutils.iml',
               '.idea/limeutils.iml',
               '.idea/limeutils.iml',
               '.idea/limeutils.iml',
               '.idea/limeutils.iml',
               '.idea/misc.xml',
               '.idea/misc.xml',
               '.idea/misc.xml',
               '.idea/misc.xml',
               '.idea/misc.xml',
               '.idea/modules.xml',
               '.idea/modules.xml',
               '.idea/modules.xml',
               '.idea/modules.xml',
               '.idea/modules.xml',
               '.idea/vcs.xml',
               '.idea/vcs.xml',
               '.idea/vcs.xml',
               '.idea/vcs.xml',
               '.idea/vcs.xml']}

install_requires = \
['hiredis>=2.0.0,<3.0.0',
 'pydantic>=1.9.1,<2.0.0',
 'pytz>=2022.1,<2023.0',
 'redis>=4.3.4,<5.0.0']

setup_kwargs = {
    'name': 'limeutils',
    'version': '0.2.12',
    'description': 'A small collection of classes and methods for dealing with Redis and more.',
    'long_description': "limeutils\n=========\n\nLimeutils is a small collection of classes and methods for dealing with Redis data and a few other helpful functions. Check out the documentation for information\n . More classes to be added as needed.\n\nThis package uses [Pydantic models][pydantic] to validate its data.\n\nInstallation\n------------\n\n### Install with `pip`\n\nThis is the recommended way to install Limeutils.\n\n```\npip install limeutils\n```\n\n### Install with repo\n\n```\npip install git+https://github.com/dropkickdev/limeutils.git@develop#egg=limeutils\n```\n\n### Install with `git clone`\n\nSimply install from the root folder\n\n```\n# This can also be a fork\ngit clone https://github.com/dropkickdev/limeutils.git\n\ncd limeutils\npip install .\n```\n\n\n[pydantic]: https://pydantic-docs.helpmanual.io/ 'Pydantic'\n\n## Documentation\n\nView the documentation at: https://dropkickdev.github.io/limeutils/\n",
    'author': 'enchance',
    'author_email': 'enchance@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dropkickdev/limeutils.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
