# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nonebot_plugin_pixivbot',
 'nonebot_plugin_pixivbot.data',
 'nonebot_plugin_pixivbot.data.pixiv_repo',
 'nonebot_plugin_pixivbot.data.source',
 'nonebot_plugin_pixivbot.data.source.mongo',
 'nonebot_plugin_pixivbot.data.source.mongo.migration',
 'nonebot_plugin_pixivbot.handler',
 'nonebot_plugin_pixivbot.handler.command',
 'nonebot_plugin_pixivbot.handler.common',
 'nonebot_plugin_pixivbot.handler.interceptor',
 'nonebot_plugin_pixivbot.model',
 'nonebot_plugin_pixivbot.model.message',
 'nonebot_plugin_pixivbot.model.old',
 'nonebot_plugin_pixivbot.protocol_dep',
 'nonebot_plugin_pixivbot.query',
 'nonebot_plugin_pixivbot.service',
 'nonebot_plugin_pixivbot.utils']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0',
 'PixivPy-Async>=1.2.14,<2.0.0',
 'lazy>=1.4,<2.0',
 'motor>=3.0.0,<4.0.0',
 'nonebot2>=2.0.0b4,<3.0.0',
 'nonebot_plugin_apscheduler>=0.1.3,<0.2.0',
 'numpy>=1.23.1,<2.0.0']

extras_require = \
{'socks': ['aiohttp-socks>=0.7.1,<0.8.0']}

setup_kwargs = {
    'name': 'nonebot-plugin-pixivbot',
    'version': '1.1.1',
    'description': 'Nonebot Plugin PixivBot',
    'long_description': 'nonebot_plugin_pixivbot\n=====\n\nPixivBot中协议无关的通用部分。\n请使用具体协议版本的插件：\n\n- [nonebot-plugin-pixivbot-onebot-v11 (Onebot V11)](https://github.com/ssttkkl/nonebot-plugin-pixivbot-onebot-v11)\n- [nonebot-plugin-pixivbot-kook (KOOK / 开黑啦)](https://github.com/ssttkkl/nonebot-plugin-pixivbot-kook)\n\n## 配置\n\n最小配置：\n```\npixiv_refresh_token=  # 前面获取的REFRESH_TOKEN\npixiv_mongo_conn_url=  # MongoDB连接URL，格式：mongodb://<用户名>:<密码>@<主机>:<端口>/<数据库>\npixiv_mongo_database_name=  # 连接的MongoDB数据库\n```\n\n完整配置（除最小配置出现的配置项以外都是可选项，给出的是默认值）（NoneBot配置项这里不列出，参考[配置 | NoneBot](https://v2.nonebot.dev/docs/tutorial/configuration#%E8%AF%A6%E7%BB%86%E9%85%8D%E7%BD%AE%E9%A1%B9)）：\n\n```\nsuperuser=[]  # 能够发送超级命令的用户（JSON数组，格式为["onebot:123456", "kaiheila:1919810"]，下同）\nblocklist=[]  # Bot不响应的用户，可以避免Bot之间相互调用（JSON数组）\n\npixiv_refresh_token=  # 前面获取的REFRESH_TOKEN\npixiv_mongo_conn_url=  # MongoDB连接URL，格式：mongodb://<用户名>:<密码>@<主机>:<端口>/<数据库>\npixiv_mongo_database_name=  # 连接的MongoDB数据库\npixiv_proxy=None  # 代理URL\npixiv_query_timeout=60  # 查询超时（单位：秒）\npixiv_simultaneous_query=8  # 向Pixiv查询的并发数\n\n# 缓存过期时间（单位：秒）\npixiv_download_cache_expires_in = 3600 * 24 * 7\npixiv_illust_detail_cache_expires_in = 3600 * 24 * 7\npixiv_user_detail_cache_expires_in = 3600 * 24 * 7\npixiv_illust_ranking_cache_expires_in = 3600 * 6\npixiv_search_illust_cache_expires_in = 3600 * 24\npixiv_search_user_cache_expires_in = 3600 * 24\npixiv_user_illusts_cache_expires_in = 3600 * 24\npixiv_user_bookmarks_cache_expires_in = 3600 * 24\npixiv_related_illusts_cache_expires_in = 3600 * 24\npixiv_other_cache_expires_in = 3600 * 6\n\npixiv_block_tags=[]  # 当插画含有指定tag时会被过滤\npixiv_block_action=no_image  # 过滤时的动作，可选值：no_image(不显示插画，回复插画信息), completely_block(只回复过滤提示), no_reply(无回复)\n\npixiv_download_quantity=original  # 插画下载品质，可选值：original, square_medium, medium, large\npixiv_download_custom_domain=None  # 使用反向代理下载插画的域名\n\npixiv_compression_enabled=False  # 启用插画压缩\npixiv_compression_max_size=None  # 插画压缩最大尺寸\npixiv_compression_quantity=None  # 插画压缩品质（0到100）\n\npixiv_query_to_me_only=False  # 只响应关于Bot的查询\npixiv_command_to_me_only=False  # 只响应关于Bot的命令\n\npixiv_query_cooldown=0  # 每次查询的冷却时间\npixiv_no_query_cooldown_users=[]  # 在这个列表中的用户不受冷却时间的影响（JSON数组）\npixiv_max_item_per_query=10  # 每个查询最多请求的插画数量\n\npixiv_tag_translation_enabled=True  # 启用搜索关键字翻译功能（平时搜索时记录标签翻译，在查询时判断是否存在对应中日翻译）\n\npixiv_more_enabled=True  # 启用重复上一次请求（还要）功能\npixiv_query_expires_in=10*60  # 上一次请求的过期时间（单位：秒）\n\npixiv_illust_query_enabled=True  # 启用插画查询（看看图）功能\n\npixiv_ranking_query_enabled=True  # 启用榜单查询（看看榜）功能\npixiv_ranking_default_mode=day  # 默认查询的榜单，可选值：day, week, month, day_male, day_female, week_original, week_rookie, day_manga\npixiv_ranking_default_range=[1, 3]  # 默认查询的榜单范围\npixiv_ranking_fetch_item=150  # 每次从服务器获取的榜单项数（查询的榜单范围必须在这个数目内）\npixiv_ranking_max_item_per_query=5  # 每次榜单查询最多能查询多少项\n\npixiv_random_illust_query_enabled=True  # 启用关键字插画随机抽选（来张xx图）功能\npixiv_random_illust_method=bookmark_proportion  # 随机抽选方法，下同，可选值：bookmark_proportion(概率与书签数成正比), view_proportion(概率与阅读量成正比), timedelta_proportion(概率与投稿时间和现在的时间差成正比), uniform(相等概率)\npixiv_random_illust_min_bookmark=0  # 过滤掉书签数小于该值的插画，下同\npixiv_random_illust_min_view=0  # 过滤掉阅读量小于该值的插画，下同\npixiv_random_illust_max_page=20  # 每次从服务器获取的查询结果页数，下同\npixiv_random_illust_max_item=500  # 每次从服务器获取的查询结果项数，下同\n\npixiv_random_recommended_illust_query_enabled=True  # 启用推荐插画随机抽选（来张图）功能\npixiv_random_recommended_illust_method=uniform\npixiv_random_recommended_illust_min_bookmark=0\npixiv_random_recommended_illust_min_view=0\npixiv_random_recommended_illust_max_page=40\npixiv_random_recommended_illust_max_item=1000\n\npixiv_random_related_illust_query_enabled=True  # 启用关联插画随机抽选（不够色）功能\npixiv_random_related_illust_method=bookmark_proportion\npixiv_random_related_illust_min_bookmark=0\npixiv_random_related_illust_min_view=0\npixiv_random_related_illust_max_page=4\npixiv_random_related_illust_max_item=100\n\npixiv_random_user_illust_query_enabled=True  # 启用用户插画随机抽选（来张xx老师的图）功能\npixiv_random_user_illust_method=timedelta_proportion\npixiv_random_user_illust_min_bookmark=0\npixiv_random_user_illust_min_view=0\npixiv_random_user_illust_max_page=2147483647\npixiv_random_user_illust_max_item=2147483647\n\npixiv_random_bookmark_query_enabled=True  # 启用用户书签随机抽选（来张私家车）功能\npixiv_random_bookmark_user_id=0  # 当QQ用户未绑定Pixiv账号时，从该Pixiv账号的书签内抽选\npixiv_random_bookmark_method=uniform\npixiv_random_bookmark_min_bookmark=0\npixiv_random_bookmark_min_view=0\npixiv_random_bookmark_max_page=2147483647\npixiv_random_bookmark_max_item=2147483647\n```\n\n## Special Thanks\n\n[Mikubill/pixivpy-async](https://github.com/Mikubill/pixivpy-async)\n\n[nonebot/nonebot2](https://github.com/nonebot/nonebot2)\n\n## LICENSE\n\n```\nMIT License\n\nCopyright (c) 2021 ssttkkl\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n\n```\n',
    'author': 'ssttkkl',
    'author_email': 'huang.wen.long@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ssttkkl/nonebot-plugin-pixivbot',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
