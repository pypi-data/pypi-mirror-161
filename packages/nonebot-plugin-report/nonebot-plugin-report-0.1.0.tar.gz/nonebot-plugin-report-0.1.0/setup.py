# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_report']

package_data = \
{'': ['*']}

install_requires = \
['nonebot2>=2.0.0-beta.4,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-report',
    'version': '0.1.0',
    'description': 'Push message to from anywhere to your bot through webhook.',
    'long_description': '<div align="center">\n\n# nonebot-plugin-report\n\nPush message to from anywhere to your bot through webhook.\n\n</div>\n\n----\n\n### 功能\n\n该插件提供了一个位于 `/report` 的 webhook，通过此路由可向 bot 推送消息，实现消息推送机器人的功能\n\n### 使用\n\nwebhook template\n```json\n// POST /report\n{\n    "token": "your token here",\n    "title": "report title",\n    "content": "report content", // *required\n    "send_to": "send to"\n}\n```\n\n##### 字段\n\n`token`: 令牌，当与设置的 `REPORT_TOKEN` 相同时才会推送消息，否则返回 403\n\n`title`: 消息标题\n\n`content`: 消息内容，必需字段\n\n`send_to`: 推送对象。若为 `null` 则推送给所有超管；若为字符串则将其视为推送对象 user_id；若为字符串列表同上\n\n##### 配置\n\n`REPORT_TOKEN`: 令牌，若不设置则不会进行验证\n\n`REPORT_ROUTE`: 推送路由，默认为 `/report`，若出现路由冲突可以更换该值\n\n### 其它\n\n- 向 webhook 发送 POST 请求\n- 仅支持发送纯文本消息\n',
    'author': 'syrinka',
    'author_email': 'syrinka@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/syrinka/nonebot-plugin-report',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
