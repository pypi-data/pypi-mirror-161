# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['max_ard', 'max_ard.commands', 'max_ard.io', 'max_ard.outputs']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.1.0,<3.0.0',
 'Shapely>=1.7.1,<2.0.0',
 'backports.cached-property>=1.0.1,<2.0.0',
 'boto3>=1.17.73,<2.0.0',
 'click>=8.0.0,<9.0.0',
 'maxar-ard-grid>=1.2.1,<2.0.0',
 'pdoc3>=0.10.0,<0.11.0',
 'pydantic>=1.7.4,<2.0.0',
 'requests-futures>=1.0.0,<2.0.0',
 'requests-oauthlib>=1.3.0,<2.0.0',
 'requests>=2.25.1,<3.0.0',
 's3fs>=0.4.2,<0.5.0']

extras_require = \
{'full': ['rasterio>=1.2.10,<2.0.0', 'Fiona>=1.8.19,<2.0.0']}

entry_points = \
{'console_scripts': ['max-ard = max_ard.commands.command:max_ard']}

setup_kwargs = {
    'name': 'max-ard',
    'version': '1.5.2',
    'description': 'ARD SDK and CLI tools',
    'long_description': '# max_ard\n\nA Python SDK and CLI for working with [Maxar ARD Imagery](https://ard.maxar.com/docs/)\n\n## Introduction\n\n`max_ard` consists of a Python SDK for selecting, ordering, and working with Maxar ARD imagery and a set of CLI tools for common tasks.\n\n## Installation\n\n`pip install max-ard`\n\n## Documentation\n\nExtensive docs are available at https://ard.maxar.com/docs/sdk/\n',
    'author': 'Marc Pfister',
    'author_email': 'marc.pfister@maxar.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ard.maxar.com/docs/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
