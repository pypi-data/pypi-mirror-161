# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['async_pixiv', 'async_pixiv.client', 'async_pixiv.model', 'async_pixiv.utils']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp-socks>=0.7.1,<0.8.0',
 'aiohttp>=3.8.1,<4.0.0',
 'arko-wrapper>=0.2.0,<0.3.0',
 'pydantic[email]>=1.9.1,<2.0.0']

extras_require = \
{'extra': ['regex>=2022.7.25,<2023.0.0', 'ujson>=5.4.0,<6.0.0'],
 'extra:sys_platform != "win32"': ['uvloop>=0.16.0,<0.17.0'],
 'full': ['regex>=2022.7.25,<2023.0.0',
          'ujson>=5.4.0,<6.0.0',
          'playwright>=1.24.0,<2.0.0'],
 'full:sys_platform != "win32"': ['uvloop>=0.16.0,<0.17.0'],
 'playwright': ['playwright>=1.24.0,<2.0.0'],
 'regex': ['regex>=2022.7.25,<2023.0.0'],
 'ujson': ['ujson>=5.4.0,<6.0.0']}

setup_kwargs = {
    'name': 'async-pixiv',
    'version': '0.0.4',
    'description': 'Async Pixiv API',
    'long_description': '# async-pixiv\nAsync Pixiv API\n\n\n## Building...',
    'author': 'Arko',
    'author_email': 'arko.space.cc@gmail.com',
    'maintainer': 'Karako',
    'maintainer_email': 'karakohear@gmail.com',
    'url': 'https://github.com/ArkoClub/async-pixiv',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
