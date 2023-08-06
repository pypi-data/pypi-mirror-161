# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['picsellia_annotations']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.1,<2.0.0', 'xmltodict>=0.13.0,<0.14.0']

setup_kwargs = {
    'name': 'picsellia-annotations',
    'version': '0.2.0',
    'description': 'Package with pydantic schemas of COCO files and VOC File and some utils to read those annotations files',
    'long_description': None,
    'author': 'Thomas Darget',
    'author_email': 'thomasdarget@hotmail.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
