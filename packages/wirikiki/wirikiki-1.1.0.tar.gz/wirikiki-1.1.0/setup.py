# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wirikiki', 'wirikiki.cli']

package_data = \
{'': ['*'],
 'wirikiki': ['config/*',
              'myKB/.git/*',
              'myKB/.git/hooks/*',
              'myKB/.git/info/*',
              'myKB/.git/logs/*',
              'myKB/.git/logs/refs/heads/*',
              'myKB/.git/objects/25/*',
              'myKB/.git/objects/78/*',
              'myKB/.git/objects/8a/*',
              'myKB/.git/objects/94/*',
              'myKB/.git/objects/d5/*',
              'myKB/.git/refs/heads/*',
              'myKB/anonymous/*',
              'myKB/fab/*',
              'web/*',
              'web/css/*',
              'web/css/imgs_dhx_material/*',
              'web/img/*',
              'web/js/*']}

install_requires = \
['aiofiles>=0.8.0,<0.9.0',
 'fastapi>=0.79.0,<0.80.0',
 'orjson>=3.7.11,<4.0.0',
 'python-jose>=3.3.0,<4.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'setproctitle>=1.3.0,<2.0.0',
 'tomli>=2.0.1,<3.0.0',
 'uvicorn>=0.18.2,<0.19.0']

entry_points = \
{'console_scripts': ['wirikiki = wirikiki.cli.wirikiki:run',
                     'wirikiki-pwgen = wirikiki.cli.wirikiki_pwgen:run']}

setup_kwargs = {
    'name': 'wirikiki',
    'version': '1.1.0',
    'description': 'A tiny desktop wiki',
    'long_description': None,
    'author': 'fdev31',
    'author_email': 'fdev31@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/fdev31/wirikiki/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
