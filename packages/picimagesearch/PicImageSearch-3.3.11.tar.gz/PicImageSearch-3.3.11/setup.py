# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['PicImageSearch', 'PicImageSearch.model']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp[speedups]>=3.8.1,<4.0.0',
 'lxml>=4.9.1,<5.0.0',
 'multidict>=6.0.2,<7.0.0',
 'pyquery>=1.4.3,<2.0.0']

extras_require = \
{'socks': ['aiohttp_socks>=0.7.1,<0.8.0']}

setup_kwargs = {
    'name': 'picimagesearch',
    'version': '3.3.11',
    'description': 'PicImageSearch APIs for Python 3.x 适用于 Python 3 以图搜源整合API',
    'long_description': '<div align="center">\n\n# PicImageSearch\n\n✨ 聚合识图引擎 用于以图搜源✨\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/kitUIN/PicImageSearch/master/LICENSE">\n    <img src="https://img.shields.io/github/license/kitUIN/PicImageSearch" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/PicImageSearch">\n    <img src="https://img.shields.io/pypi/v/PicImageSearch" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7+-blue" alt="python">\n  <a href="https://github.com/kitUIN/PicImageSearch/releases">\n    <img src="https://img.shields.io/github/v/release/kitUIN/PicImageSearch" alt="release">\n  </a>\n  <a href="https://github.com/kitUIN/PicImageSearch/issues">\n    <img src="https://img.shields.io/github/issues/kitUIN/PicImageSearch" alt="release">\n  </a>\n </p>\n<p align="center">\n  <a href="https://www.kituin.fun/wiki/picimagesearch/">📖文档</a>\n  ·\n  <a href="https://github.com/kitUIN/PicImageSearch/issues/new">🐛提交建议</a>\n</p>\n\n## 支持\n\n- [x] [SauceNAO](https://saucenao.com/)\n- [x] [TraceMoe](https://trace.moe/)\n- [x] [Iqdb](http://iqdb.org/)\n- [x] [Ascii2D](https://ascii2d.net/)\n- [x] [Google谷歌识图](https://www.google.com/imghp)\n- [x] [BaiDu百度识图](https://graph.baidu.com/)\n- [x] [E-Hentai](https://e-hentai.org/)\n- [x] [ExHentai](https://exhentai.org/)\n- [x] 同步/异步\n\n## 简要说明\n\n详细见[文档](https://www.kituin.fun/wiki/picimagesearch/) 或者[`demo`](https://github.com/kitUIN/PicImageSearch/tree/main/demo)  \n`同步`请使用`from PicImageSearch.sync import ...`导入  \n`异步`请使用`from PicImageSearch import Network,...`导入  \n**推荐使用异步**  \n\n## 简单示例\n\n```python\nfrom loguru import logger\nfrom PicImageSearch import SauceNAO, Network\n\nasync with Network() as client:  # 可以设置代理 Network(proxies=\'scheme://host:port\')\n    saucenao = SauceNAO(client=client, api_key="your api key")  # client, api_key 不能少\n    url = "https://raw.githubusercontent.com/kitUIN/PicImageSearch/main/demo/images/test01.jpg"\n    resp = await saucenao.search(url=url)\n    # 搜索本地图片\n    # file = open(r"demo/images/test01.jpg", "rb")\n    # resp = await saucenao.search(file=file)\n\n    logger.info(resp.status_code)  # HTTP 状态码\n    # logger.info(resp.origin)  # 原始数据\n    logger.info(resp.raw[0].origin)\n    logger.info(resp.long_remaining)\n    logger.info(resp.short_remaining)\n    logger.info(resp.raw[0].thumbnail)\n    logger.info(resp.raw[0].similarity)\n    logger.info(resp.raw[0].hidden)\n    logger.info(resp.raw[0].title)\n    logger.info(resp.raw[0].author)\n    logger.info(resp.raw[0].url)\n    logger.info(resp.raw[0].pixiv_id)\n    logger.info(resp.raw[0].member_id)\n```\n\n```python\nfrom PicImageSearch.sync import SauceNAO\n\nsaucenao = SauceNAO(api_key="your api key")  # api_key 不能少\nurl = "https://raw.githubusercontent.com/kitUIN/PicImageSearch/main/demo/images/test01.jpg"\nresp = saucenao.search(url=url)\n# 搜索本地图片\n# file = open(r"demo/images/test01.jpg", "rb")\n# resp = saucenao.search(file=file)\n# 下面操作与异步方法一致\n```\n\n### 安装\n\n- 此包需要 Python 3.7 或更新版本。\n- `pip install PicImageSearch`\n- 或者\n- `pip install PicImageSearch -i https://pypi.tuna.tsinghua.edu.cn/simple`\n\n## Star History\n\n[![Star History](https://starchart.cc/kitUIN/PicImageSearch.svg)](https://starchart.cc/kitUIN/PicImageSearch)\n',
    'author': 'kitUIN',
    'author_email': 'kulujun@gmail.com',
    'maintainer': 'kitUIN',
    'maintainer_email': 'kulujun@gmail.com',
    'url': 'https://github.com/kitUIN/PicImageSearch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
