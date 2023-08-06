# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_apscheduler']

package_data = \
{'': ['*']}

install_requires = \
['apscheduler>=3.7.0,<4.0.0', 'nonebot2>=2.0.0-alpha.8,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-apscheduler',
    'version': '0.1.4',
    'description': 'APScheduler Support for NoneBot2',
    'long_description': '<p align="center">\n  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>\n</p>\n\n<div align="center">\n\n# NoneBot Plugin APScheduler\n\n_✨ NoneBot APScheduler 定时任务插件 ✨_\n\n</div>\n\n<p align="center">\n  <a href="https://raw.githubusercontent.com/nonebot/plugin-apscheduler/master/LICENSE">\n    <img src="https://img.shields.io/github/license/nonebot/plugin-apscheduler.svg" alt="license">\n  </a>\n  <a href="https://pypi.python.org/pypi/nonebot-plugin-apscheduler">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-apscheduler.svg" alt="pypi">\n  </a>\n  <img src="https://img.shields.io/badge/python-3.7+-blue.svg" alt="python">\n</p>\n\n## 使用方式\n\n加载插件后使用 `require` 获取 `scheduler` 对象（请注意插件加载顺序）\n\n```python\nfrom nonebot import require\n\nscheduler = require("nonebot_plugin_apscheduler").scheduler\n\n@scheduler.scheduled_job("cron", hour="*/2", id="xxx", args=[1], kwargs={arg2: 2})\nasync def run_every_2_hour(arg1, arg2):\n    pass\n\nscheduler.add_job(run_every_day_from_program_start, "interval", days=1, id="xxx")\n```\n\n## 配置项\n\n### apscheduler_autostart\n\n是否自动启动 `scheduler`\n\n### apscheduler_log_level\n\n`int` 类型日志等级\n\n- `WARNING` = `30` (默认)\n- `INFO` = `20`\n- `DEBUG` = `10` (只有在开启 nonebot 的 debug 模式才会显示 debug 日志)\n\n### apscheduler_config\n\n`apscheduler` 的相关配置。参考 [配置 scheduler](https://apscheduler.readthedocs.io/en/latest/userguide.html#scheduler-config), [配置参数](https://apscheduler.readthedocs.io/en/latest/modules/schedulers/base.html#apscheduler.schedulers.base.BaseScheduler)\n\n配置需要包含 `prefix: apscheduler.`\n\n默认配置：\n\n```json\n{ "apscheduler.timezone": "Asia/Shanghai" }\n```\n',
    'author': 'yanyongyu',
    'author_email': 'yyy@nonebot.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nonebot/plugin-apscheduler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
