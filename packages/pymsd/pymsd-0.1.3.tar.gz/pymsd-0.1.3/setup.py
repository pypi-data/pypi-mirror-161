# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymsd', 'pymsd.proto']

package_data = \
{'': ['*']}

install_requires = \
['grpcio>=1.46.3,<2.0.0', 'numpy>=1.23.1,<2.0.0', 'protobuf==3.20.1']

setup_kwargs = {
    'name': 'pymsd',
    'version': '0.1.3',
    'description': 'the python sdk of msd-rs',
    'long_description': "the python sdk of [msd-rs](https://github.com/msd-rs/msd-rs)\n\nAlthough grpc can be used at any time, through [msd-proto](https://github.com/msd-rs/msd-proto) to generate client code to connect to the `msd` service, `msd-sdk-python` Simplifies the process and provides some handy helper functions to make calling easier\n\n尽管任何时候都可以使用 grpc, 通过 [msd-proto](https://github.com/msd-rs/msd-proto)  来生成连接 `msd` 服务的客户端代码，`msd-sdk-python` 简化了这个过程, 并提供了一些方便的辅助函数, 使得调用更加容易\n\n## 安装 (Install)\n\n```\npip install pymsd\n```\n\n## 使用 (Usage)\n\n### 快速上手 (QuickStart)\n\n```python\nimport pymsd\n\n# msd 服务的地址 | msd server address\nHOST='127.0.0.1:50051'\n\ndf = pymsd.msd_query(HOST, 'select * from kline1d.sh600000')\n# 或者使用异步模式 | or use aysnc mode\n# df = await pymsd.msd_query_async(HOST, 'select * from kline1d.sh600000')\n\n# to_pandas_dataframe 将结果集转换为 pandas.DataFrame, 需要 pandas 已经安装 | use `to_pandas_dataframe` covert result to pandas.DataFrame\n# to_polars_dataframe 将结果集转换为 polars.DataFrame, 需要 polars 已经安装 | use `to_polars_dataframe` covert result to polars.DataFrame\n# to_numpy_list 将结果集转换为[(名字, numpy.ndarray)], 需要 numpy 已经安装  | use `to_numpy_list` covert result to list of (name, numpy.ndarray) \ndf = pymsd.to_pandas_dataframe(df)\nprint(df)\n\n```\n\n### 自建连接\npymsd 提供了简单接口, 使用全局的服务连接, 也可以自建连接, 这时会有更好的控制\n\npymsd provides a simple interface, using the global service connection, you can also build your own connection, then there will be better control\n\n```python\nimport pymsd\nimport grpc\n\n# 创建 grpc 连接 | create grpc connection\nwith grpc.insecure_channel(_HOST) as channel:\n    stub = pymsd.DataFrameServiceStub(channel)\n\n    # 创建请求 | new request\n    req = pymsd.GetDataFrameRequest()\n    req.sql = sql\n\n    # 触发请求 | invoke request\n    resp = stub.Get(req)\n    # df 即是返回的结果集, 可以根据不同的需要, 将其转换成 pandas.DataFrame 等等 | df is the result, that can be convert to pandas.DataFrame etc.\n    df = resp.values\n```",
    'author': 'LiJia',
    'author_email': 'lijia.c@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/msd-rs/msd-sdk-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
