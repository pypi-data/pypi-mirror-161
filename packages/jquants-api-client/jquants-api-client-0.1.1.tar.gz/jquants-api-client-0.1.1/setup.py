# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jquantsapi']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.23.0,<3.0.0',
 'types-python-dateutil>=2.8.19,<3.0.0',
 'types-requests>=2.28.5,<3.0.0',
 'urllib3>=1.24.3,<2.0.0']

extras_require = \
{':python_full_version >= "3.7.1" and python_version < "3.8"': ['pandas>=1.3.5,<1.4.0',
                                                                'numpy>=1.21.6,<1.22.0'],
 ':python_version >= "3.8"': ['pandas>=1.4.3,<2.0.0', 'numpy>=1.23.1,<2.0.0']}

setup_kwargs = {
    'name': 'jquants-api-client',
    'version': '0.1.1',
    'description': 'J-Quants API Client Library',
    'long_description': '# jquants-api-client\n\n[![PyPI version](https://badge.fury.io/py/jquants-api-client.svg)](https://badge.fury.io/py/jquants-api-client)\n\n個人投資家向けデータAPI配信サービス「 [J-Quants API](https://jpx-jquants.com/#jquants-api) 」のPythonクライアントライブラリです。\nJ-QuantsやAPI仕様についての詳細を知りたい方は [公式ウェブサイト](https://jpx-jquants.com/) をご参照ください。\n現在、J-Quants APIはベータ版サービスとして提供されています。\n\n## 使用方法\npip経由でインストールします。\n\n```shell\npip install jquants-api-client\n```\n\n\n### J-Quants API のリフレッシュトークン取得\n\nJ-Quants APIを利用するためには [J-Quants API の Web サイト](https://jpx-jquants.com/#jquants-api) から取得できる\nリフレッシュトークンが必要になります。\n\n### サンプルコード\n\n```python\nfrom datetime import datetime\nfrom dateutil import tz\nimport jquantsapi\n\nmy_refresh_token:str = "*****"\ncli = jquantsapi.Client(refresh_token=my_refresh_token)\ndf = cli.get_price_range(\n    start_dt=datetime(2022, 7, 25, tzinfo=tz.gettz("Asia/Tokyo")),\n    end_dt=datetime(2022, 7, 26, tzinfo=tz.gettz("Asia/Tokyo")),\n)\nprint(df)\n```\nAPIレスポンスがDataframeの形式で取得できます。\n```shell\n       Code       Date  ...  AdjustmentClose  AdjustmentVolume\n0     13010 2022-07-25  ...           3630.0            8100.0\n1     13050 2022-07-25  ...           2023.0           54410.0\n2     13060 2022-07-25  ...           2001.0          943830.0\n3     13080 2022-07-25  ...           1977.5          121300.0\n4     13090 2022-07-25  ...          43300.0             391.0\n...     ...        ...  ...              ...               ...\n4189  99930 2022-07-26  ...           1426.0            5600.0\n4190  99940 2022-07-26  ...           2605.0            7300.0\n4191  99950 2022-07-26  ...            404.0           13000.0\n4192  99960 2022-07-26  ...           1255.0            4000.0\n4193  99970 2022-07-26  ...            825.0          133600.0\n\n[8388 rows x 14 columns]\n```\n\n## 対応API\n\n### ラッパー群\u3000 \nJ-Quants API の各APIエンドポイントに対応しています。\n  - get_id_token\n  - get_listed_info\n  - get_listed_sections\n  - get_market_segments\n  - get_prices_daily_quotes\n  - get_fins_statements\n  - get_fins_announcement\n### ユーティリティ群\n日付範囲を指定して一括でデータ取得して、取得したデータを結合して返すようなユーティリティが用意されています。\n  - get_list\n  - get_price_range\n  - get_statements_range\n\n\n## 動作確認\nPython 3.10で動作確認を行っています。\nJ-Quants APIは現在β版のため、本ライブラリも今後仕様が変更となる可能性があります。\n\n## 開発\nJ-Quants API Clientの開発に是非ご協力ください。\nGithub上でIssueやPull Requestをお待ちしております。\n',
    'author': 'J-Quants Project Contributors',
    'author_email': 'j-quants@jpx.co.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/J-Quants/jquants-api-client-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
