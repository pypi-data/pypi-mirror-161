# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['YetAnotherPicSearch']

package_data = \
{'': ['*']}

install_requires = \
['PicImageSearch>=3.3.10,<4.0.0',
 'aiohttp[speedups]>=3.8.1,<4.0.0',
 'arrow>=1.2.2,<2.0.0',
 'diskcache>=5.4.0,<6.0.0',
 'lxml>=4.9.1,<5.0.0',
 'nonebot-adapter-onebot>=2.1.1,<3.0.0',
 'nonebot2>=2.0.0b4,<3.0.0',
 'pyquery>=1.4.3,<2.0.0',
 'tenacity>=8.0.1,<9.0.0',
 'yarl>=1.7.2,<2.0.0']

setup_kwargs = {
    'name': 'yetanotherpicsearch',
    'version': '1.5.17',
    'description': 'Yet Another Picture Search Nonebot Plugin',
    'long_description': '<div align="center">\n\n# YetAnotherPicSearch\n\n[![license](https://img.shields.io/github/license/NekoAria/YetAnotherPicSearch)](https://raw.githubusercontent.com/NekoAria/YetAnotherPicSearch/master/LICENSE)\n![python](https://img.shields.io/badge/python-3.8+-blue)\n[![release](https://img.shields.io/github/v/release/NekoAria/YetAnotherPicSearch)](https://github.com/NekoAria/YetAnotherPicSearch/releases)\n\n基于 [nonebot2](https://github.com/nonebot/nonebot2) 及 [PicImageSearch](https://github.com/kitUIN/PicImageSearch) 的另一个 Nonebot 搜图插件\n\n</div>\n\n## 项目简介\n\n主要受到 [cq-picsearcher-bot](https://github.com/Tsuk1ko/cq-picsearcher-bot) 的启发。我只需要基础的搜图功能，于是忍不住自己也写了一个，用来搜图、搜番、搜本子。\n\n目前支持的搜图服务：\n\n- [saucenao](https://saucenao.com)\n- [ascii2d](https://ascii2d.net)\n- [iqdb](https://iqdb.org)\n- [exhentai](https://exhentai.org)\n- [whatanime](https://trace.moe)\n\n目前适配的是 `OneBot V11` ，没适配 QQ 频道。\n\n## 文档目录\n\n- [使用教程](docs/使用教程.md)\n- [部署教程](docs/部署教程.md)\n\n## 效果预览\n\n<p float="left">\n    <img src="docs/images/image01.jpg" width="32%" />\n    <img src="docs/images/image02.jpg" width="32%" />\n    <img src="docs/images/image03.jpg" width="32%" />\n</p>\n\n## 感谢名单\n\n- [cq-picsearcher-bot](https://github.com/Tsuk1ko/cq-picsearcher-bot)\n- [PicImageSearch](https://github.com/kitUIN/PicImageSearch)\n',
    'author': 'NekoAria',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NekoAria/YetAnotherPicSearch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
