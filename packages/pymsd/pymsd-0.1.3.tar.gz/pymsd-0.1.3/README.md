the python sdk of [msd-rs](https://github.com/msd-rs/msd-rs)

Although grpc can be used at any time, through [msd-proto](https://github.com/msd-rs/msd-proto) to generate client code to connect to the `msd` service, `msd-sdk-python` Simplifies the process and provides some handy helper functions to make calling easier

尽管任何时候都可以使用 grpc, 通过 [msd-proto](https://github.com/msd-rs/msd-proto)  来生成连接 `msd` 服务的客户端代码，`msd-sdk-python` 简化了这个过程, 并提供了一些方便的辅助函数, 使得调用更加容易

## 安装 (Install)

```
pip install pymsd
```

## 使用 (Usage)

### 快速上手 (QuickStart)

```python
import pymsd

# msd 服务的地址 | msd server address
HOST='127.0.0.1:50051'

df = pymsd.msd_query(HOST, 'select * from kline1d.sh600000')
# 或者使用异步模式 | or use aysnc mode
# df = await pymsd.msd_query_async(HOST, 'select * from kline1d.sh600000')

# to_pandas_dataframe 将结果集转换为 pandas.DataFrame, 需要 pandas 已经安装 | use `to_pandas_dataframe` covert result to pandas.DataFrame
# to_polars_dataframe 将结果集转换为 polars.DataFrame, 需要 polars 已经安装 | use `to_polars_dataframe` covert result to polars.DataFrame
# to_numpy_list 将结果集转换为[(名字, numpy.ndarray)], 需要 numpy 已经安装  | use `to_numpy_list` covert result to list of (name, numpy.ndarray) 
df = pymsd.to_pandas_dataframe(df)
print(df)

```

### 自建连接
pymsd 提供了简单接口, 使用全局的服务连接, 也可以自建连接, 这时会有更好的控制

pymsd provides a simple interface, using the global service connection, you can also build your own connection, then there will be better control

```python
import pymsd
import grpc

# 创建 grpc 连接 | create grpc connection
with grpc.insecure_channel(_HOST) as channel:
    stub = pymsd.DataFrameServiceStub(channel)

    # 创建请求 | new request
    req = pymsd.GetDataFrameRequest()
    req.sql = sql

    # 触发请求 | invoke request
    resp = stub.Get(req)
    # df 即是返回的结果集, 可以根据不同的需要, 将其转换成 pandas.DataFrame 等等 | df is the result, that can be convert to pandas.DataFrame etc.
    df = resp.values
```