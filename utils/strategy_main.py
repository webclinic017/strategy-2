import datetime

import backtrader as bt
import pandas as pd
from redis import Redis

from utils.strategy_analyzers import TradeList
from utils.strategy_func import (
    deal_date_from_str,
    get_data_from_akshare,
    process_trade_list,
)


def common_main(
    class_id: str,
    user_id: str,
    experiment_id: str,
    strategy_class: str,
    from_time: str,
    to_time: str,
    code: str,
    cash: float,
    rdb: Redis,
    comm: float = 0.0005,
):
    # 打开交易记录
    cerebro = bt.Cerebro(tradehistory=True)
    # 添加策略
    cerebro.addstrategy(strategy_class)
    # 添加分析者
    cerebro.addanalyzer(TradeList, _name="trade_list")
    # 准备数据
    from_time = deal_date_from_str(from_time)
    to_time = deal_date_from_str(to_time)
    params = dict(
        fromdate=datetime.datetime(from_time[0], from_time[1], from_time[2]),
        todate=datetime.datetime(to_time[0], to_time[1], to_time[2]),  # 2021, 7, 6
        timeframe=bt.TimeFrame.Days,
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=6,
    )
    # 获取股票数据
    df = get_data_from_akshare(symbol=code)
    # 导入股票数据
    feed = bt.feeds.PandasDirectData(dataname=df, **params)

    # 添加合约数据
    cerebro.adddata(feed, name=f"{code}")
    cerebro.broker.setcommission(commission=comm)

    # 添加资金
    cerebro.broker.setcash(cash)
    cerebro.addanalyzer(bt.analyzers.Returns, _name="Returns")
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name="AnnualReturn")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="DrawDown")
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="SharpeRatio")

    # 添加分析者
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name="TimeReturn")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="Returns")

    results = cerebro.run()
    strategy_result = results[0]

    # 最终资金，收益率，最大回撤，夏普比率，年化收益率
    strategy_result_dict = {
        "result_asset": cerebro.broker.getvalue(),
        "return": strategy_result.analyzers.Returns.get_analysis()["rtot"],
        "max_drawdown": strategy_result.analyzers.DrawDown.get_analysis()["drawdown"],
        "sharpe_ratio": strategy_result.analyzers.SharpeRatio.get_analysis()[
            "sharperatio"
        ],
        "annual_return": strategy_result.analyzers.Returns.get_analysis()["rnorm"],
    }

    # 打印每次交易的信息
    pnl = pd.Series(strategy_result.analyzers.TimeReturn.get_analysis())  # 累计收益率
    cumulative = (pnl + 1).cumprod()
    cumulative.index = [item.isoformat() for item in cumulative.index.date]
    cumulative.name = "value"
    cumulative.index.name = "datetime"
    data_json = cumulative.to_json()
    save_result = rdb.set(f"{class_id}_{user_id}_{experiment_id}_value", data_json)
    rdb.expire(f"{class_id}_{user_id}_{experiment_id}_value", 600)
    strategy_result_dict.update({"save_value_redis": save_result})

    # 打印交易详情
    trade_list = strategy_result.analyzers.trade_list.get_analysis()
    df = pd.DataFrame(trade_list)
    df.drop(["pnl", "pnl / bar", "ticker"], axis=1, inplace=True)
    trade_detail = process_trade_list(df, comm)
    # print(trade_detail)
    data_json = trade_detail.to_json(orient="records")
    save_result = rdb.set(f"{class_id}_{user_id}_{experiment_id}_detail", data_json)
    rdb.expire(f"{class_id}_{user_id}_{experiment_id}_detail", 600)
    strategy_result_dict.update({"save_detail_redis": save_result})

    return strategy_result_dict
