# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_hammer_nbnhhsh']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<0.24.0', 'nonebot-plugin-hammer-core>=0.1.1,<0.2.0']

setup_kwargs = {
    'name': 'nonebot-plugin-hammer-nbnhhsh',
    'version': '1.0.0',
    'description': 'a nonebot2 plugin to request "nbnhhsh" api for qq group',
    'long_description': '<p align="center">\n  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>\n</p>\n\n<div align="center">\n\n# Nonebot Plugin Hammer Nbnhhsh\n\n✨ 基于onebot、nonebot2与「好好说话」项目的 字母/数字缩写含义查询及提交插件 ✨\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/ArgonarioD/nonebot-plugin-hammer-nbnhhsh/main/LICENSE">\n    <img src="https://img.shields.io/github/license/ArgonarioD/nonebot-plugin-hammer-core" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot-plugin-hammer-nbnhhsh">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-hammer-nbnhhsh.svg" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.9-blue.svg" alt="python">\n  <img src="https://img.shields.io/badge/Onebot-v11-lightgrey" alt="onebot11">\n  <img src="https://img.shields.io/badge/nonebot-2.0.0b4-orange" alt="nonebot2">\n  <a href="https://github.com/ArgonarioD/nonebot-plugin-hammer-core">\n    <img src="https://img.shields.io/badge/hammer--core-0.1.1-green" alt="hammer-core">\n  </a>\n</p>\n\n## 使用本插件\n\n### 1. 使用nb-cli安装（推荐）\n\n在命令行中执行`nb plugin install nonebot-plugin-hammer-nbnhhsh`安装即可\n\n### 2. 使用包管理工具安装（用pip举例）\n\n1. 在命令行中执行`pip install nonebot-plugin-hammer-nbnhhsh`安装python包\n2. 在`bot.py`中添加`nonebot.load_plugin(\'nonebot-plugin-hammer-nbnhhsh\')`\n\n## 命令\n> 注：\n>  - 本节中的命令省略了命令前缀，本插件的命令前缀采用了`.env`文件配置中的`COMMAND_START`的值，默认情况下是`/`，也就是说，在你没有自行配置过`.env`文件的情况下，本插件提供的命令如`/nbnhhsh <一段话>`\n>  - 在下文中，“缩写”的定义为“仅由字母或阿拉伯数字中任意一种或两种所构成的长度大于1的连续字符串\n\n| 命令                       | 说明                                             |\n|--------------------------|------------------------------------------------|\n| nbnhhsh <一段话>            | 查询该段话中所有缩写所代表的含义                               |\n| nbnhhsh.submit <缩写> <含义> | 为「好好说话」项目贡献词条，“含义”末尾可通过括号包裹（简略注明来源），经人工审核将整理录入 |\n\n## 主要功能效果\n例命令（`COMMAND_START`配置为默认值）：\n```\n/nbnhhsh u1s1，nsdd，但是你有没有想过ababa是怎么想的，nm有，nzzhnzz\n```\n机器人回复：\n```\n- u1s1:\n 有一说一\n- nsdd:\n 你说的对 你是对的 你是弟弟 诺森德岛 你萨顶顶 你神叨叨 你手短短 南山大道 泥塑敦敦 你射得多 你塞蛋蛋 泥兽段段 你屎多多 你是大雕 男神代代 扭扭捏捏 你耍大刀 你水多多 你稍等等 内射到顶 铃声多多\n- nm:\n 纳米 你妈 你妹 农民 normal Nicki Minaj 柠檬 奶妈 妮妙 诺民（NCT成员李帝努和罗渽民的cp） no miss 嫩模 Nuclear missile 牛马 尼玛（网络） 你没事吧 匿名 内幕（网络） 年迈 nano machine\n- ababa 有可能是:\n Ababa\n- nzzhnzz:\n 尚未录入，可以自行使用"/nbnhhsh.submit nzzhnzz <含义>"命令提交对应文字\n```\n## 测试环境\n- Python 3.9\n- go-cqhttp v1.0.0-rc3\n- nonebot 2.0.0-beta.4\n\n## 鸣谢\n\n- [onebot](https://github.com/botuniverse/onebot)\n- [nonebot2](https://github.com/nonebot/nonebot2)\n- [能不能好好说话？](https://github.com/itorr/nbnhhsh)\n\n---\n~~*如果觉得有用的话求点个Star啵QwQ*~~',
    'author': 'ArgonarioD',
    'author_email': '739062975@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://docs.hammer-hfut.tk:233',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
