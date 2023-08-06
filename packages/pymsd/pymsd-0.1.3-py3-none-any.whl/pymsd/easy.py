import pymsd
import grpc

_HOST = ''
_SYNC_CHANNEL: grpc.Channel = None
_ASYNC_CHANNEL: grpc.aio.Channel = None

def msd_query(host: str, sql: str) -> pymsd.DataFrame:

    global _HOST, _SYNC_CHANNEL
    if host != _HOST:
        if _SYNC_CHANNEL != None:
            _SYNC_CHANNEL.close()
        _HOST = host
        _SYNC_CHANNEL = grpc.insecure_channel(_HOST, None, 2)
    if _SYNC_CHANNEL is None:
        _SYNC_CHANNEL = grpc.insecure_channel(_HOST, None, 2)

    assert _SYNC_CHANNEL is not None

    stub = pymsd.DataFrameServiceStub(_SYNC_CHANNEL)
    req = pymsd.GetDataFrameRequest()
    req.sql = sql
    resp = stub.Get(req)
    return resp.values

async def msd_async_query(host: str, sql: str) -> pymsd.DataFrame:
    global _HOST, _ASYNC_CHANNEL
    if host != _HOST:
        if _SYNC_CHANNEL != None:
            _ASYNC_CHANNEL.close()
        _HOST = host
        _ASYNC_CHANNEL = grpc.aio.insecure_channel(_HOST, None, 2)
    if _ASYNC_CHANNEL is None:
        _ASYNC_CHANNEL = grpc.aio.insecure_channel(_HOST, None, 2)

    stub = pymsd.DataFrameServiceStub(_ASYNC_CHANNEL)
    req = pymsd.GetDataFrameRequest()
    req.sql = sql
    resp = await stub.Get(req)
    return resp.values
