import backtrader as bt


class MyBaseStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)

    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                self.log(
                    "buy,{},{},{},{}".format(
                        order.executed.price,
                        order.executed.price * order.executed.size,
                        order.executed.comm,
                        self.broker.getposition(self.data).size,
                    )
                )

            else:  # Sell
                self.log(
                    "sell,{},{},{},{}".format(
                        order.executed.price,
                        -order.executed.price * order.executed.size,
                        order.executed.comm,
                        self.broker.getposition(self.data).size,
                    )
                )


class MAStrategy(MyBaseStrategy):

    def __init__(self):
        # 一般用于计算指标或者预先加载数据，定义变量使用
        self.short_ma = bt.indicators.SMA(self.datas[0].close, period=self.short_window)
        self.long_ma = bt.indicators.SMA(self.datas[0].close, period=self.long_window)

    def next(self):
        size = self.getposition(self.datas[0]).size
        # 做多
        if (
            size == 0
            and self.short_ma[-1] < self.long_ma[-1]
            and self.short_ma[0] > self.long_ma[0]
        ):
            # 1手=100股，满仓买入
            if len(self.data) < self.data.buflen():
                ss = int((self.broker.getcash() / 100) / self.datas[0].close[1]) * 100
                self.order = self.buy(self.data, size=ss)
        # 平多
        if (
            size > 0
            and self.short_ma[-1] > self.long_ma[-1]
            and self.short_ma[0] < self.long_ma[0]
        ):
            self.close(self.datas[0])


class BollStrategy(MyBaseStrategy):
    # 可配置策略参数
    params = dict(
        # p_period_volume=10,  # 前n日最大交易量
        # p_sell_ma=5,  # 跌破该均线卖出
        p_oneplot=False,  # 是否打印到同一张图
    )

    def __init__(self):
        self.inds = dict()
        for i, d in enumerate(self.datas):
            self.inds[d] = dict()
            # 布林线中轨
            boll_mid = bt.ind.BBands(d.close).mid
            # 买入条件
            self.inds[d]["buy_con"] = bt.And(
                # 突破中轨
                d.open < boll_mid,
                d.close > boll_mid,
                # 放量
                d.volume
                == bt.ind.Highest(d.volume, period=self.p_period_volume, plot=False),
            )
            # 卖出条件
            self.inds[d]["sell_con"] = d.close < bt.ind.SMA(
                d.close, period=self.p_sell_ma
            )

    def next(self):
        for i, d in enumerate(self.datas):
            dt, dn = self.datetime.date(), d._name  # 获取时间及股票代码
            pos = self.getposition(d).size
            if not pos:  # 不在场内，则可以买入
                if self.inds[d]["buy_con"]:  # 如果金叉
                    ss = (
                        int((self.broker.getcash() / 100) / self.datas[0].close[1])
                        * 100
                    )
                    self.buy(data=d, size=ss)  # 买买买
            elif self.inds[d]["sell_con"]:  # 在场内，且死叉
                self.close(data=d)  # 卖卖卖
