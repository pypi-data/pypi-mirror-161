# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pkiviewer',
 'pkiviewer.model',
 'pkiviewer.model.extension',
 'pkiviewer.model.public_key',
 'pkiviewer.oid',
 'pkiviewer.utils',
 'pkiviewer.view',
 'pkiviewer.view.display',
 'pkiviewer.view.display.extension',
 'pkiviewer.view.display.public_key']

package_data = \
{'': ['*']}

modules = \
['py']
install_requires = \
['click>=8.1.3,<9.0.0',
 'cryptography>=37.0.4,<38.0.0',
 'rich>=12.5.1,<13.0.0',
 'tomli>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['pkiviewer = pkiviewer.__main__:run']}

setup_kwargs = {
    'name': 'pkiviewer',
    'version': '0.1.0',
    'description': 'PKI Viewer',
    'long_description': None,
    'author': 'Simon Kennedy',
    'author_email': 'sffjunkie+code@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
