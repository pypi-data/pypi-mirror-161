# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nonebot_plugin_pixivbot_kook',
 'nonebot_plugin_pixivbot_kook.protocol_dep',
 'nonebot_plugin_pixivbot_kook.utils']

package_data = \
{'': ['*']}

install_requires = \
['asyncache>=0.1.1,<0.2.0',
 'cachetools>=5.2.0,<6.0.0',
 'nonebot-adapter-kaiheila>=0.0.4,<0.0.5',
 'nonebot-plugin-pixivbot>=1.1.1,<1.2.0',
 'nonebot2>=2.0.0-beta.4,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-pixivbot-kook',
    'version': '1.1.1',
    'description': 'Nonebot Plugin Pixivbot (KOOK)',
    'long_description': 'nonebot-plugin-pixivbot-kook\n=====\n\nKOOK (原开黑啦) 协议版本的PixivBot\n\n## 配置\n\n额外配置：\n```\n# KOOK服务器鉴权策略，用于schedule等命令（可选值：nobody, everyone, must_have_permission）\npixiv_kook_admin_strategy=nobody\n\n# 若上一项为must_have_permission，该项指明用户具有什么权限才能通过鉴权\n# 参考：https://developer.kaiheila.cn/doc/http/channel\npixiv_kook_admin_must_have_permission=0\n\n# 权限信息缓存时限（单位：秒）\n# 使用缓存可避免每次鉴权都发送多次网络请求，但会导致权限更新无法及时反映，设置为0禁用缓存\npixiv_kook_admin_permission_cache_ttl=2*60*60\n```\n\n## Special Thanks\n\n[Mikubill/pixivpy-async](https://github.com/Mikubill/pixivpy-async)\n\n[nonebot/nonebot2](https://github.com/nonebot/nonebot2)\n\n\n## LICENSE\n\n```\nMIT License\n\nCopyright (c) 2022 ssttkkl\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n\n```\n',
    'author': 'ssttkkl',
    'author_email': 'huang.wen.long@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ssttkkl/nonebot-plugin-pixivbot-kook',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
