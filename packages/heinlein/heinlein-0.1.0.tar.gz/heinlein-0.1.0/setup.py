# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['heinlein',
 'heinlein.dataset',
 'heinlein.dtypes',
 'heinlein.manager',
 'heinlein.region',
 'heinlein.utilities']

package_data = \
{'': ['*'],
 'heinlein.dataset': ['configs/*',
                      'configs/configs_bkp/*',
                      'configs/support/*']}

install_requires = \
['Shapely>=1.8.2,<2.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'astropy>=5.1,<6.0',
 'numpy>=1.23.1,<2.0.0',
 'pandas>=1.4.3,<2.0.0',
 'portalocker>=2.5.1,<3.0.0',
 'pymongo>=4.2.0,<5.0.0']

entry_points = \
{'console_scripts': ['heinlein = heinlein.cmds:main']}

setup_kwargs = {
    'name': 'heinlein',
    'version': '0.1.0',
    'description': 'Library for interacting with large astronomical survey datasets',
    'long_description': None,
    'author': 'Patrick Wells',
    'author_email': 'pwells@ucdavis.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
