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

        size = self.position.size
        # 做多
        if (
            size == 0
            and self.short_ma[-1] < self.long_ma[-1]
            and self.short_ma[0] > self.long_ma[0]
        ):
            # 1手=100股，满仓买入
            if len(self.data) < self.data.buflen():
                ss = int((self.broker.get_cash() * (1-self.broker.comminfo[None].p.commission) / 100) / self.datas[0].open[1]) * 100
                self.order = self.buy(self.data, size=ss)
        # 平多
        if (
            size > 0
            and self.short_ma[-1] > self.long_ma[-1]
            and self.short_ma[0] < self.long_ma[0]
        ):
            self.close(self.datas[0])


class BollingerBandsStrategy(MyBaseStrategy):

    def __init__(self):
        self.bbands = bt.indicators.BollingerBands(
            self.data.close,
            period=self.period,
            devfactor=self.devfactor
        )

    def next(self):
        if not self.position:  # 没有仓位
            if self.data.close[0] < self.bbands.lines.bot[0]:  # 当价格低于布林带下轨时
                # 预留手续费，例如佣金为0.1%，印花税为0.1%
                ss = int((self.broker.get_cash() * (1-self.broker.comminfo[None].p.commission) / 100) / self.datas[0].open[1]) * 100
                self.buy(self.data, size=ss)  # 全仓买入
        elif self.data.close[0] > self.bbands.lines.top[0]:  # 当价格高于布林带上轨时
            self.sell(size=self.position.size)  # 全仓卖出


class KDJStrategy(MyBaseStrategy):

    def __init__(self):
        self.bbands = bt.indicators.BollingerBands(
            self.data.close,
            period=self.period,
            devfactor=self.devfactor
        )

    def next(self):
        if not self.position:  # 没有仓位
            if self.data.close[0] < self.bbands.lines.bot[0]:  # 当价格低于布林带下轨时
                # 预留手续费，例如佣金为0.1%，印花税为0.1%
                ss = int((self.broker.get_cash() * (1-self.broker.comminfo[None].p.commission) / 100) / self.datas[0].open[1]) * 100
                self.buy(self.data, size=ss)  # 全仓买入
        elif self.data.close[0] > self.bbands.lines.top[0]:  # 当价格高于布林带上轨时
            self.sell(size=self.position.size)  # 全仓卖出
