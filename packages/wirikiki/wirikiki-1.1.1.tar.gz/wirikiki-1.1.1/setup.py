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
    'version': '1.1.1',
    'description': 'A tiny desktop wiki',
    'long_description': '_Wirikiki_ aims at being a productivity oriented **markdown notebook**.\nIt\'s compatible with the most common features supported by GitHub\'s markdown and adds a few other.\n\nIn comparison to [Jupyter](https://jupyter.org/) it lacks the python notes but brings:\n\n- speed / **light** footprint\n- **simplicity** of use\n- **uncluttered** UI supporting both **dark & bright modes**\n- more **advanced markdown support** via [markItDown](https://markitdown.netlify.app/) and plugins and [Marked](https://marked.js.org/) for the editor\n- auto **archival** (using git)\n\n# Installation\n\n## Building\n\n3 alternative ways to get a runnable code:\n\n- download a release (TODO)\n- `make dev`\n- manual installation\n\n```\nsh ./makevueApps.sh\nnpm install\nDIST=1 ./node_modules/.bin/rollup -c rollup.config.js\n```\n\n# Usage\n\n## Create one wiki\n\n```\nwirikiki new myNewWiki\n```\n\n## Run the wiki\n\nGo to the newly created folder "myNewWiki" and run:\n\n```\nwirikiki\n```\n\n## Zero-install mode\n\nYou can just open the html file to get a degraded experience, data will not be saved.\n\n## Keyboard shortcuts\n\n| Key            | Description                                     |\n| -------------- | ----------------------------------------------- |\n| **Escape**     | Close editor or modal, else toggles the sidebar |\n| **Del**        | **D**elete current page                         |\n| **E**          | **E**dit current note                           |\n| **F**          | Search/**F**ind something                       |\n| **N**          | **C**reate a new note                           |\n| **Left/Right** | Switch to previous/next note                    |\n\n# Advanced usage\n\nBasic git support is provided, to enable it just type `git init` in the `myKB` folder.\n\n```shell\ncd myKB\ngit init\n```\n\n# Dependencies\n\n- **Python 3**\n  - if you want to run it **without the virtualenv** you will need the following python packages:\n    - aiofiles\n    - fastapi\n    - uvicorn\n- nodejs and npm (BUILD ONLY)\n- inotify-tools (DEV ONLY)\n\n# Developers note\n\nThis is built using\n[Vue.js version 3](https://v3.vuejs.org/) for the front\nand [FastAPI](https://fastapi.tiangolo.com/) for the server side.\n',
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
