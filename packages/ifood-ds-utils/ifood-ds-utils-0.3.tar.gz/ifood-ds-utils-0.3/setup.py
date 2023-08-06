# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ifood_ds_utils']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'colorama>=0.4.5,<0.5.0',
 'directory-tree>=0.0.2,<0.0.3',
 'ifood-aws-login==2.4.8']

entry_points = \
{'console_scripts': ['ifood-ds-utils = ifood_ds_utils.main:version',
                     'mlgo_template = '
                     'ifood_ds_utils.main:create_ifood_mlgo_template',
                     's3_template = '
                     'ifood_ds_utils.main:create_ifood_s3_template',
                     'upload-folder-s3 = ifood_ds_utils.main:upload_to_s3']}

setup_kwargs = {
    'name': 'ifood-ds-utils',
    'version': '0.3',
    'description': '',
    'long_description': None,
    'author': 'Javier Daza',
    'author_email': 'javier.olivella@ifood.com',
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
