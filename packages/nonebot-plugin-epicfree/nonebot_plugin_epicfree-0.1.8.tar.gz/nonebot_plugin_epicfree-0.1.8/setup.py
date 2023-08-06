# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_epicfree']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.0.0',
 'nonebot-adapter-onebot>=2.0.0b1',
 'nonebot-plugin-apscheduler>=0.1.0',
 'nonebot2>=2.0.0a14']

setup_kwargs = {
    'name': 'nonebot-plugin-epicfree',
    'version': '0.1.8',
    'description': 'A Epic free game info plugin for Nonebot2',
    'long_description': '<h1 align="center">Nonebot Plugin EpicFree</h1></br>\n\n\n<p align="center">🤖 用于获取 Epic 限免游戏资讯的 Nonebot2 插件</p></br>\n\n\n<p align="center">\n  <a href="https://github.com/monsterxcn/nonebot_plugin_epicfree/actions">\n    <img src="https://img.shields.io/github/workflow/status/monsterxcn/Typecho-Theme-VOID/Build?style=flat-square" alt="actions">\n  </a>\n  <a href="https://raw.githubusercontent.com/monsterxcn/nonebot_plugin_epicfree/master/LICENSE">\n    <img src="https://img.shields.io/github/license/monsterxcn/nonebot_plugin_epicfree?style=flat-square" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot_plugin_epicfree">\n    <img src="https://img.shields.io/pypi/v/nonebot_plugin_epicfree?style=flat-square" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7.3+-blue?style=flat-square" alt="python"><br />\n</p></br>\n\n\n**安装方法**\n\n\n使用以下命令之一快速安装（若配置了 PyPI 镜像，你可能无法及时检索到插件最新版本）：\n\n\n``` zsh\nnb plugin install nonebot_plugin_epicfree\n\npip install --upgrade nonebot_plugin_epicfree\n```\n\n\n重启 Bot 即可体验此插件。\n\n\n<details><summary><i>关于 nonebot2 及相关依赖版本</i></summary></br>\n\n\n此插件在以下两种环境测试通过！\n\n\n```\n# 文件夹拷贝方式安装\nnonebot2.0.0.a16 nonebot-adapter-cqhttp==2.0.0a16\n\n# 命令行 / 脚手架安装\nnonebot2.0.0.b2 nonebot-adapter-onebot==2.0.0b1\n```\n\n\n此插件在 nonebot2.0.0.b1 下可能不兼容，需要参考 [commit `44f4bf8`](https://github.com/monsterxcn/nonebot_plugin_epicfree/commit/44f4bf8c3c578fff242a106a28b85884c78a0404) 自行修改 `__init__.py` 中 `T_State` 的写法。\n\n在已淘汰的 Nonebot2 适配器 [nonebot-adapter-cqhttp](https://pypi.org/project/nonebot-adapter-cqhttp/) 下，通过拷贝文件夹 `nonebot_plugin_epicfree` 至 Nonebot2 插件目录、手动安装 `nonebot-plugin-apscheduler` 和 `httpx` 依赖后仍可正常启用此插件。在未来某个版本会完全移除该适配器支持，请尽快升级至 `nonebot-adapter-onebot`。\n\n以上述命令行方式安装本插件时，可能由于依赖版本差异报错。对于新手，推荐在安装插件前备份当前环境依赖版本，以便后续恢复：\n\n\n```bash\n# 备份当前的依赖版本\npip3 freeze > requirements.txt\n\n# 尝试安装 nonebot_plugin_epicfree\n\n# 若安装出错，可尝试恢复之前备份的依赖版本\npip3 install -r requirements.txt\n```\n\n\n</details>\n\n\n<details><summary><i>单独加载此插件</i></summary></br>\n\n\n在 Nonebot2 入口文件（例如 `bot.py`）增加：\n\n\n``` python\nnonebot.load_plugin("nonebot_plugin_epicfree")\n```\n\n\n</details>\n\n\n**使用方法**\n\n\n```python\n# nonebot_plugin_epicfree/__init__.py#L27\nepicMatcher = on_regex("((E|e)(P|p)(I|i)(C|c))?喜(加一|\\+1)")\n\n# nonebot_plugin_epicfree/__init__.py#L34\nepicSubMatcher = on_regex("喜(加一|\\+1)(私聊)?订阅")\n```\n\n\n发送「喜加一」查找游戏，群组内发送「喜加一订阅」订阅限免游戏资讯。基于正则匹配，所以，甚至「EpIc喜+1」这样的指令都可用！（\n\n限免游戏资讯订阅功能默认在插件文件夹内生成配置文件。但建议自行指定用于存放订阅配置的文件夹，将其写入 `resources_dir` 环境变量即可。注意该文件夹需要包含一个名为 `epicfree` 的子文件夹。在 Nonebot2 `.env` 中填写时注意去除结尾的 `/`，如果是 Windows 系统应写成形如 `D:/path/to/resources_dir`。\n\n限免游戏资讯订阅默认每周六 08:08:08 发送，如需自定义请在 `.env` 中添加格式如下的配置，其中四个数字依次代表 `day_of_week` `hour` `minute` `second`。\n\n\n```\nresources_dir="/data/bot/resources"\nepic_scheduler="5 8 8 8"\n```\n\n\n**特别鸣谢**\n\n\n[@nonebot/nonebot2](https://github.com/nonebot/nonebot2/) | [@Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp) | [@DIYgod/RSSHub](https://github.com/DIYgod/RSSHub) | [@SD4RK/epicstore_api](https://github.com/SD4RK/epicstore_api)\n\n\n> 作者是 Nonebot 新手，代码写的较为粗糙，欢迎提出修改意见或加入此插件开发！溜了溜了...\n',
    'author': 'monsterxcn',
    'author_email': 'monsterxcn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monsterxcn/nonebot_plugin_epicfree',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0',
}


setup(**setup_kwargs)
