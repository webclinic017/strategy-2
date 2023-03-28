from typing import Optional

import uvicorn
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from redis import Redis

from app.database import get_rdb
from utils.strategy_engine import MAStrategy, BollingerBandsStrategy
from utils.strategy_factory import create_class
from utils.strategy_main import common_main

app = FastAPI()


def _():
    MAStrategy, BollingerBandsStrategy
    pass


class DefaultMAParams(BaseModel):
    """
    默认 data 数据模型
    """
    strategy_name: str = "MAStrategy"
    short_window: int = 5
    long_window: int = 10


@app.post("/strategy")
def strategy(
    class_id: str = "1",
    user_id: str = "1",
    experiment_id: str = "1",
    code: str = "000001",
    from_time: str = "20200101",
    to_time: str = "20230101",
    cash: float = "1000000.0",
    rdb: Redis = Depends(get_rdb),
    data: Optional[dict] = dict(DefaultMAParams()),  # 后面设置为 None
):
    """
    本接口主要通过 post 方法传入相关参数
    其中 data 的格式为：
    ```
    MA 策略参数
    {
      "strategy_name": "MAStrategy",  # 策略名称，此处支持已有的参数模板
      "short_window": 5,  # 快速移动平均线时间参数
      "long_window": 10  # 慢速移动平均线时间参数
    }

    BollingerBandsStrategy 策略参数
    {
      "strategy_name": "BollingerBandsStrategy",  # 策略名称，此处支持已有的参数模板
      "period": 20,  # 时间参数
      "devfactor": 2,  # 倍数
    }

    KDJ 策略参数
    {
      "strategy_name": "KDJStrategy",  # 策略名称，此处支持已有的参数模板
      "k_period": 9,  # 快速随机值
      "d_period": 3,  # 慢速随机值
      "j_period": 3  # 变动速度指标
    }

    MACD 策略参数
    {
      "strategy_name": "MACDStrategy",  # 策略名称，此处支持已有的参数模板
      "period_me1": 12,  # 快速平滑移动平均线Ema时间参数
      "period_me2": 26,  # 慢速平滑移动平均线Ema时间参数(
      "period_signal": 9  # macd的时间参数n
    }

    RSI 策略参数
    {
      "strategy_name": "RSIStrategy",  # 策略名称，此处支持已有的参数模板
      "period": 14,  # rsi的时间参数n
      "top": 70,  # 买入策略
      "down": 30  # 卖出策略
    }
    ```
    :param class_id: 班级id
    :param user_id: 用户id
    :param experiment_id: 实验id
    :param code: 股票代码
    :param from_time: 开始回测时间
    :param to_time: 结束回测时间
    :param cash: 初始资金
    :param rdb: Redis 数据库
    :param data: 策略参数
    :return: 回测结果
    """
    if data:
        kwargs = data
    else:
        kwargs = dict(DefaultMAParams())
    result = common_main(
        class_id=class_id,
        user_id=user_id,
        experiment_id=experiment_id,
        strategy_class=create_class(**kwargs),
        from_time=from_time,
        to_time=to_time,
        code=code,
        cash=cash,
        rdb=rdb,
    )
    return result


# @app.get("/strategy_ma")
# def strategy_ma(
#     class_id: str = "1",
#     user_id: str = "1",
#     experiment_id: str = "1",
#     code: str = "000001",
#     from_time: str = "20200101",
#     to_time: str = "20230101",
#     cash: float = "1000000.0",
#     rdb: Redis = Depends(get_rdb),
#     short_window: int = 5,
#     long_window: int = 10,
# ):
#     """
#     MA 策略
#     :return:
#     """
#     result = common_main(
#         class_id=class_id,
#         user_id=user_id,
#         experiment_id=experiment_id,
#         strategy_class=create_class(
#             MAStrategy,
#             short_window=short_window,
#             long_window=long_window,
#         ),
#         from_time=from_time,
#         to_time=to_time,
#         code=code,
#         cash=cash,
#         rdb=rdb,
#     )
#     return result
#
#
# @app.get("/strategy_boll")
# def strategy_boll(
#     class_id: str = "1",
#     user_id: str = "1",
#     experiment_id: str = "1",
#     code: str = "000001",
#     from_time: str = "20200101",
#     to_time: str = "20230101",
#     cash: float = "1000000.0",
#     rdb: Redis = Depends(get_rdb),
#     p_period_volume: int = 10,
#     p_sell_ma: int = 5,
# ):
#     """
#     MA 策略
#     :return:
#     """
#     result = common_main(
#         class_id=class_id,
#         user_id=user_id,
#         experiment_id=experiment_id,
#         strategy_class=create_class(
#             BollStrategy,
#             p_period_volume=p_period_volume,
#             p_sell_ma=p_sell_ma,
#         ),
#         from_time=from_time,
#         to_time=to_time,
#         code=code,
#         cash=cash,
#         rdb=rdb,
#     )
#     return result


if __name__ == "__main__":
    uvicorn.run("main:app")
