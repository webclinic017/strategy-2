from redis import Redis, ConnectionPool
from app.settings import RDBSettings


rdb_settings = RDBSettings()


def get_rdb() -> Redis:
    """
    获取 Redis 连接池
    :return: 外汇 symbol 和代码映射
    :rtype: dict
    """
    pool = ConnectionPool(host=rdb_settings.host, port=rdb_settings.port, db=rdb_settings.db)
    rdb = Redis(connection_pool=pool, decode_responses=True, encoding="utf-8")
    try:
        yield rdb
    finally:
        rdb.close()
