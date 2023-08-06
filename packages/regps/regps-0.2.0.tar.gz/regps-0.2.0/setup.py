# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['regps']

package_data = \
{'': ['*']}

install_requires = \
['ExifRead>=3.0.0,<4.0.0',
 'Pillow>=9.2.0,<10.0.0',
 'exif>=1.3.5,<2.0.0',
 'gpsphoto>=2.2.3,<3.0.0',
 'piexif>=1.1.3,<2.0.0']

setup_kwargs = {
    'name': 'regps',
    'version': '0.2.0',
    'description': '',
    'long_description': None,
    'author': 'mcgillij',
    'author_email': 'mcgillivray.jason@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
