# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fugle_trade']

package_data = \
{'': ['*']}

install_requires = \
['fugle-trade-core==0.3.1',
 'keyring==23.5.0',
 'keyrings.cryptfile==1.3.8',
 'websocket-client==1.2.1']

setup_kwargs = {
    'name': 'fugle-trade',
    'version': '0.3.1',
    'description': '',
    'long_description': '# Fugle Trade Python SDK\n\n## 事前準備\n\n可以參考 https://developer.fugle.tw/docs/trading/prerequisites 完成申請金鑰相關步驟\n\n## QuickStart\n\n```python\nfrom configparser import ConfigParser\nfrom fugle_trade.sdk import SDK\nfrom fugle_trade.order import OrderObject\nfrom fugle_trade.constant import (APCode, Trade, PriceFlag, BSFlag, Action)\n\nconfig = ConfigParser()\nconfig.read(\'./config.ini\')\nsdk = SDK(config)\nsdk.login()\n\norder = OrderObject(\n    buy_sell = Action.Buy,\n    price = 28.00,\n    stock_no = "2884",\n    quantity = 2,\n    ap_code = APCode.Common\n)\nsdk.place_order(order)\n\n```\n\n## Detail\n\n所有 function 跟 response 可以在專屬文件頁查到相關資訊\n\nhttps://developer.fugle.tw/docs/trading/reference/python\n\n\n## License\n\n[MIT](LICENSE)\n',
    'author': 'Fortuna Intelligence Co., Ltd.',
    'author_email': 'development@fugle.tw',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fugle-dev/fugle-trade-python#readme',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
