import pandas as pd
import akshare as ak
import numpy as np


# 获取数据
def get_data_from_akshare(symbol: str = "000001") -> pd.DataFrame:
    # 从 AKShare 获取数据
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=symbol)
    # 对查询出来的数据进行数据处理
    stock_zh_a_hist_df.rename(
        columns={
            "日期": "datetime",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
        },
        inplace=True,
    )
    stock_zh_a_hist_df = stock_zh_a_hist_df[
        ["datetime", "open", "high", "low", "close", "volume"]
    ]
    # 补充 `openinterest` 字段
    stock_zh_a_hist_df["openinterest"] = np.nan
    stock_zh_a_hist_df.sort_values("datetime", inplace=True, ignore_index=True)
    stock_zh_a_hist_df.index = pd.to_datetime(stock_zh_a_hist_df["datetime"])
    stock_zh_a_hist_df = stock_zh_a_hist_df[
        ["open", "high", "low", "close", "volume", "openinterest"]
    ]
    return stock_zh_a_hist_df


# 处理时间格式
def deal_date_from_iso(date: str = "2022-02-13") -> list:
    year, mouth, day = date.split("-", 2)
    a = [int(year), int(mouth), int(day)]
    return a


def deal_date_from_str(date: str = "20220213") -> list:
    year, mouth, day = date[:4], date[4:6], date[6:]
    a = [int(year), int(mouth), int(day)]
    return a


def process_trade_list(
    trade_list_df: pd.DataFrame, comm: float = 0.0005
) -> pd.DataFrame:
    temp_df = trade_list_df
    buy_df = temp_df[
        [
            "dir",
            "datein",
            "pricein",
            "size",
            "value",
        ]
    ].copy()
    buy_df["comm"] = buy_df["pricein"] * buy_df["size"] * comm
    buy_df["dir"] = "buy"
    buy_df["value"] = buy_df["pricein"] * buy_df["size"]
    buy_df.columns = [
        "交易方向",
        "成交时间",
        "单价",
        "持股数量",
        "总价",
        "手续费",
    ]
    sell_df = temp_df[
        [
            "dir",
            "dateout",
            "priceout",
            "size",
            "value",
        ]
    ].copy()
    sell_df["comm"] = sell_df["priceout"] * sell_df["size"] * comm
    sell_df["dir"] = "sell"
    sell_df["value"] = sell_df["priceout"] * sell_df["size"]
    sell_df.columns = [
        "交易方向",
        "成交时间",
        "单价",
        "持股数量",
        "总价",
        "手续费",
    ]
    all_df = pd.concat([buy_df, sell_df], ignore_index=True)
    all_df.sort_values(["成交时间"], inplace=True, ignore_index=True)
    all_df = all_df[
        [
            "成交时间",
            "交易方向",
            "单价",
            "持股数量",
            "总价",
            "手续费",
        ]
    ]
    all_df.rename(
        columns={
            "成交时间": "trade_date",
            "交易方向": "trade_direction",
            "单价": "trade_price",
            "持股数量": "trade_volume",
            "总价": "trade_value",
            "手续费": "trade_comm",
        },
        inplace=True,
    )
    return all_df
