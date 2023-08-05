# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_setu', 'nonebot_plugin_setu.dao']

package_data = \
{'': ['*']}

install_requires = \
['httpx-socks>=0.7.3,<0.8.0',
 'httpx>=0.23.0,<0.24.0',
 'nonebot-adapter-onebot>=2.0.0b1,<3.0.0',
 'nonebot2>=2.0.0b2,<3.0.0',
 'tqdm>=4.61.0,<5.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-setu',
    'version': '1.1.3',
    'description': '基于lolicon api的涩图插件',
    'long_description': '\n\n\n\n<div align="center">\n    <img src="https://s4.ax1x.com/2022/03/05/bw2k9A.png" alt="bw2k9A.png" border="0"/>\n    <h1>nonebot_plugin_setu</h1>\n    <b>基于nonebot2、loliconApi的涩图插件</b>\n    <br/>\n    <a href="https://github.com/ayanamiblhx/nonebot_plugin_setu/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/ayanamiblhx/nonebot_plugin_setu?color=%09%2300BFFF&style=flat-square"></a>\n    <a href="https://github.com/ayanamiblhx/nonebot_plugin_setu/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/ayanamiblhx/nonebot_plugin_setu?color=Emerald%20green&style=flat-square"></a>\n    <a href="https://github.com/ayanamiblhx/nonebot_plugin_setu/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/ayanamiblhx/nonebot_plugin_setu?color=%2300BFFF&style=flat-square"></a>\n    <a href="https://github.com/ayanamiblhx/nonebot_plugin_setu/blob/main/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/ayanamiblhx/nonebot_plugin_setu?color=Emerald%20green&style=flat-square"></a>\n</div>\n\n## 安装及更新\n\n- 使用`nb plugin install nonebot_plugin_setu`或者`pip install nonebot_plugin_setu`来进行安装\n- 使用`nb plugin update nonebot_plugin_setu`或者`pip install nonebot_plugin_setu -U`来进行更新\n\n\n\n## 使用方式\n\n首先运行一遍robot，然后在robot目录的data目录下修改setu_config.json配置文件，然后重启robot\n\n<p align="center">\n    <a href="https://asciinema.org/a/488190"><img src="https://pan.freeload.icu/api/v3/file/source/61/setu_config.svg?sign=HE8H1qVEnrLJtPgTtiXtjW0LXdQ29NScguGy2-iNK64%3D%3A0"/></a>\n</p>\n\n### 添加配置\n\n- **在你的setu_config.json文件中修改如下配置：**\n\n  SUPERUSERS = ["主人的qq号"]，可添加多个\n\n  PROXIES_HTTP = \'HTTP魔法地址(例如`http://127.0.0.1:7890`)，这与你使用的魔法有关\'\n\n  PROXIES_SOCKS = \'SOCKS5魔法地址(例如`socks5://127.0.0.1:10808`)，这与你使用的魔法有关\'\n\n  **注**：若没有魔法或者不会设置可不填\n\n- **导入插件(两种方式二选一)**\n  \n  - 在`bot.py`中添加`nonebot.load_plugin("nonebot_plugin_setu")`\n  \n  - 在`pyproject.toml`里的`[tool.nonebot]`中添加`plugins = ["nonebot_plugin_setu"]`\n  \n  **注**：如果你使用`nb`安装插件，则不需要设置此项\n\n\n\n### 正式使用\n\n| 命令                               | 举例                                | 说明                                                                                   |\n|----------------------------------|-----------------------------------|:-------------------------------------------------------------------------------------|\n| 下载涩图/色图+数量                       | 下载涩图12345、下载色图12345               | 下载涩图：下载非涩涩图片；下载色图：下载色色图片                                                             |\n| 涩图、setu、无内鬼、色图                   | setu                              | 发送图片                                                                                 |\n| @用户cd+时间（秒）                      | @张三cd12345                        | 指定用户cd                                                                               |\n| 群cd+时间（秒）                        | 群cd12345                          | 指定群cd                                                                                |\n| 开启/关闭在线发图                        | 开启在线发图                            | 在线发图开启之后，图片将不再从本地发送而是从网上下载后在线发送，不会占用服务器存储资源                                          |\n| 开启/关闭魔法                          | 关闭魔法                              | 魔法关闭之后，图片的下载以及在线发送将不再通过魔法而是通过镜像来完成，如果没有魔法或者不会设置推荐关闭                                  |\n| 涩图tagA和B和C（最多指定三个tag）            | 涩图tag碧蓝航线、涩图tag公主连结和白丝            | 为了保证尽可能多地获取tag指定的内容，tag指定的图片都会在线获取而不从本地寻找，是否存储依然遵循在线发图开关                             |\n| 撤回间隔+时间（秒）                       | 撤回间隔20、撤回间隔0                      | 设置撤回间隔之后，机器人将会在指定间隔后撤回发送的图片，撤回间隔为0时，机器人将不会进行撤回。同时撤回间隔以群聊为单位，每个群都能设置不同的间隔，私聊将不会触发撤回操作 |\n| 涩图api、设置api地址+`服务器ip地址或域名:机器人端口` | 涩图api、设置api地址`123.456.789.0:8080` | 设置api并开放防火墙端口之后，就能把服务器中的图库数据转为api供他人调用，本地api调试请访问`http://localhost:机器人端口/setu/docs`  |\n| 开启涩涩、开启私聊涩涩、关闭涩涩、关闭私聊涩涩          | 开启涩涩、开启私聊涩涩                       | 开启涩涩之后，机器人将会发送色色图片，涩涩以群聊为单位，支持不同群是否开启                                                |\n| 涩图帮助                             | 涩图帮助                              | 获取命令列表                                                                               |\n\n#### 注：\n\n- 用户cd和群cd同时存在时，以用户cd为准\n- 群cd默认3600s\n- 开放api时请保证机器人监听的地址为0.0.0.0\n- 仅好友才能私聊发图，私聊发图时若未指定用户cd，则默认cd3600s\n\n## TODO\n\n- [x] 选择`在线/下载`发图\n- [x] 指定群CD和用户CD\n- [x] 是否使用PROXY\n- [x] 指定TAG\n- [x] 自建图库并开放api\n- [x] 自动撤回\n- [x] 开启涩涩\n- [ ] 数据可视化\n\n\n\n## 更新日志\n### 2022/7/29[v1.1.2]\n\n- 增加帮助，修复下载图片失败bug\n\n### 2022/4/2[v1.0.14]\n\n- 新增自动撤回\n- 新增自建图库与图库api\n- 新增涩涩模式\n\n\n\n### 2022/3/19[v1.0.11]\n\n- 新增指定tag，可指定tag进行发图，tag最多指定三个\n\n\n\n### 2022/3/17[v1.0.9]\n\n- 新增在线发图开关，图片可以在线发送而不占用服务器存储空间\n- 新增魔法开关，没有魔法也能够正常使用\n\n注：旧版本用户请删除setu_config.json然后重新配置一遍\n\n\n\n### 2022/3/13[v1.0.5]\n\n- 删除SETU_CD，修改cd配置，不再依赖userscd.json，转为依赖数据库文件\n- 添加用户cd和群cd，可由管理员进行指定和更改\n- 引入数据库存储图片信息，修改图片存储格式从jpg转为图片原本对应样式\n\n注：旧版本用户请删除setu_config.json然后重新配置一遍\n\n\n\n### 2022/3/9[v1.0.4]\n\n- 更改异常捕获范围，修复无法捕获异常的bug\n\n\n\n### 2022/3/8[v1.0.3]\n\n- 删除配置：SETU_NUM，可下载指定数量的图片\n- 新增下载图片进度条\n\n\n\n### 2022/3/5 [v1.0.1]\n\n- 支持nonebot[v2.0.0-beta2]，请更新至最新版nonebot使用\n- 更改图片的名字为对应pid\n- 更改文件的配置方式，不再依赖.env文件\n\n\n\n### 2022/1/26 [v1.0.0a1]\n\n- 支持nonebot[v2.0.0-beta1]，beta1之前的请使用0.0.6版本\n',
    'author': 'ayanamiblhx',
    'author_email': '1196818079@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ayanamiblhx/nonebot_plugin_setu',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
