# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_what2eat']

package_data = \
{'': ['*'], 'nonebot_plugin_what2eat': ['resource/*']}

install_requires = \
['httpx>=0.23.0,<0.24.0',
 'nonebot-adapter-onebot>=2.1.1,<3.0.0',
 'nonebot-plugin-apscheduler>=0.1.3,<0.2.0',
 'nonebot2>=2.0.0b3,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-what2eat',
    'version': '0.3.3a2',
    'description': 'Ask bot for what to eat today!',
    'long_description': '<div align="center">\n    <img width="200" src="starving_logo.gif" alt="logo">\n\n# What to Eat/Drink\n\n<!-- prettier-ignore-start -->\n<!-- markdownlint-disable-next-line MD036 -->\n_🧃🧋🍔🌮🍜🍮🍣🍻🍩 今天吃/喝什么 🍩🍻🍣🍮🍜🌮🍔🧋🧃_\n<!-- prettier-ignore-end -->\n\n</div>\n\n<p align="center">\n  \n  <a href="https://github.com/MinatoAquaCrews/nonebot_plugin_what2eat/blob/beta/LICENSE">\n    <img src="https://img.shields.io/github/license/MinatoAquaCrews/nonebot_plugin_what2eat?color=blue">\n  </a>\n  \n  <a href="https://github.com/nonebot/nonebot2">\n    <img src="https://img.shields.io/badge/nonebot2-2.0.0b3+-green">\n  </a>\n  \n  <a href="https://github.com/MinatoAquaCrews/nonebot_plugin_what2eat/releases/tag/v0.3.3a2">\n    <img src="https://img.shields.io/github/v/release/MinatoAquaCrews/nonebot_plugin_what2eat?color=orange">\n  </a>\n\n  <a href="https://www.codefactor.io/repository/github/MinatoAquaCrews/nonebot_plugin_what2eat">\n    <img src="https://img.shields.io/codefactor/grade/github/MinatoAquaCrews/nonebot_plugin_what2eat/beta?color=red">\n  </a>\n  \n</p>\n\n## 版本\n\nv0.3.3a2 今天喝什么！\n\n⚠ 适配nonebot2-2.0.0b3+\n\n[更新日志](https://github.com/MinatoAquaCrews/nonebot_plugin_what2eat/releases/tag/v0.3.3a2)\n\n## 安装\n\n1. 通过`pip`或`nb`安装；\n\n2. 数据默认位于`./resource`下`eating.json`、`drinks.json`与`greetings.json`，可通过设置`env`下`WHAT2EAT_PATH`更改；基础菜单、群特色菜单及群友询问Bot次数会记录在该文件中：\n\n    ```python\n    WHAT2EAT_PATH="your-path-to-resource"\n    ```\n\n## 功能\n\n1. 选择恐惧症？让Bot建议你今天吃/喝什么！\n\n2. ⚠ 插件配置：\n   \n    ``` python\n    WHAT2EAT_PATH="your-path-to-resource"         # 资源路径\n    USE_PRESET_MENU=false                         # 是否从repo中下载预置基础菜单，默认为False\n    USE_PRESET_GREETINGS=false                    # 是否从repo中下载预置问候语，默认为False\n    EATING_LIMIT=5                                # 每个时段吃什么的次数上限，默认5次；每日6点、11点、17点、22点自动刷新\n    GREETING_GROUPS_ID=["123456789", "987654321"] # 默认开启小助手群组，或{"123456789", "987654321"}\n    SUPERUSERS={"12345678"}                       # 同nonebot超管配置\n    ```\n\n3. 群管理可自行添加或移除群特色菜单（位于`eating.json`下`[group_food][group_id]`）；超管可添加或移除基础菜单（`[basic_food]`）；\n\n4. 各群特色菜单相互独立；各群每个时间段询问Bot建议次数独立；Bot会综合各群菜单+基础菜单给出建议；\n\n5. 吃饭小助手：每天7、12、15、18、22点群发问候语提醒群友吃饭/摸鱼/下班，`GREETING_GROUPS_ID`设置常开的群号列表（或集合），每次启动插件时将置`True`，形如：\n\n    ```python\n    GREETING_GROUPS_ID=["123456789", "987654321"] # 名字长防止与其他插件配置名相同\n    ```\n\n    ⚠ 群吃饭小助手启用配置存于`greetings.json`的`groups_id`字段\n\n6. 初次使用该插件时，若不存在`eating.json`与`greetings.json`文件，设置`USE_PRESET_MENU`及`USE_PRESET_GREETINGS`可从仓库中尝试下载；若下载失败则会报错。会尝试从仓库中下载`drinks.json`。\n\n    ```python\n    USE_PRESET_MENU=false\n    USE_PRESET_GREETINGS=false\n    ```\n\n    ⚠ 若存在`eating.json`与`greetings.json`，不会从仓库中下载，仅检查是否缺少必要的键值，并补写初始键值\n\n    ⚠ 从仓库下载会**覆写**原有配置！建议老用户按需开启从仓库下载设置\n\n    ⚠ `v0.3.2`会兼容`v0.2.x`，在插件启动时启用自动兼容：检测`v0.2.x`的配置文件，将其自动改为当前版本的配置文件及键值。但当原`v0.2.x`的配置文件不存在时则忽略。`v0.3.3`已弃用兼容，请注意\n\n## 命令\n\n1. 吃什么：今天吃什么、中午吃啥、今晚吃啥、中午吃什么、晚上吃啥、晚上吃什么、夜宵吃啥……\n\n2. 🔥 **新增** 喝什么： 今天喝什么、中午喝啥、今晚喝啥、中午喝什么、晚上喝啥、晚上喝什么、夜宵喝啥……\n\n\t⚠ 喝什么与吃什么共用`EATING_LIMIT`次数\n\n3. [管理员或超管] 添加或移除群菜名：[添加/移除 菜名]；\n\n4. 查看群菜单：[菜单/群菜单/查看菜单]；\n\n6. [超管] 添加至基础菜单：[加菜 菜名]；\n\n7. 查看基础菜单：[基础菜单]；\n\n8. [管理员或超管] 开启/关闭吃饭小助手：[开启/启用/关闭/禁用小助手]；\n\n9. [管理员或超管] 添加/删除吃饭小助手问候语：[添加/删除/移除问候 时段 问候语]；\n\n    ⚠ 添加/移除问候操作可一步步进行，或一次性输入两或三个命令；可中途取消操作\n\n## 效果\n\n1. 示例1\n\n    Q：今晚吃什么\n\n    A：建议肯德基\n\n    （吃什么*5）\n\n    Q：今晚吃什么\n\n    A：你今天已经吃得够多了！\n\n    Q：群菜单\n\n    A：\n\n    ---群特色菜单---\n\n    alpha\n\n    beta\n\n    gamma\n\n2. 示例2\n\n    [群管] Q：添加 派蒙\n\n    A：派蒙 已加入群特色菜单~\n\n    [超管] Q：加菜 东方馅挂炒饭\n\n    A：东方馅挂炒饭 已加入基础菜单~\n\n    [群管] Q：移除 东方馅挂炒饭\n\n    A：东方馅挂炒饭 在基础菜单中，非超管不可操作哦~\n\n3. 示例3\n\n    [群管] Q：添加问候\n\n    A：请输入添加问候语的时段，可选：早餐/午餐/摸鱼/晚餐/夜宵，输入取消以取消操作\n\n    [群管] Q：摸鱼\n\n    A：请输入添加的问候语，输入取消以取消操作\n\n    [群管] Q：你好\n\n    A：你好 已加入 摸鱼问候~\n\n## 本插件改自\n\n[HoshinoBot-whattoeat](https://github.com/pcrbot/whattoeat)\n\n部分菜名参考[程序员做饭指南](https://github.com/Anduin2017/HowToCook)',
    'author': 'KafCoppelia',
    'author_email': 'k740677208@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
