"""
类工厂
"""
from utils.strategy_engine import (
    MAStrategy,
    BollingerBandsStrategy,
    KDJStrategy,
    MACDStrategy,
    RSIStrategy,
)


def create_class(strategy_name, **kwargs):
    my_class = type(
        "MyStrategy",
        (eval(strategy_name),),
        kwargs,
    )
    return my_class


if __name__ == "__main__":
    print(MAStrategy)
    print(BollingerBandsStrategy)
    print(KDJStrategy)
    print(MACDStrategy)
    print(RSIStrategy)
