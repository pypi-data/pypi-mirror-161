from quantplay.utils.constant import TickInterval
from quantplay.strategy.base import QuantplayAlgorithm
from quantplay.service import market
from quantplay.order_execution.mean_price import MeanPriceExecutionAlgo

class Shifu(QuantplayAlgorithm):
    def __init__(self):
        self.interval = TickInterval.minute
        self.entry_time = "14:30"
        self.exit_time = "9:25"
        self.strategy_trigger_times = [self.entry_time]
        self.exchange_to_trade_on = "NSE"
        self.stream_symbols_by_security_type = {
            "EQ": market.symbols("FNO_STOCKS")
        }

        self.strategy_type = "overnight"
        self.strategy_tag = "shifu"
        self.holding_days = 1
        self.data_required_for_days = 20
        self.execution_algo = MeanPriceExecutionAlgo(7)

        super(Shifu, self).__init__()

    def get_trades(self, market_data):
        equity_data = market_data[market_data.security_type == "EQ"]

        market.add_intraday_metrics(equity_data, "09:29", self.entry_time)
        trades = market.get_trades(equity_data, entry_time_regex=self.entry_time)

        trades = market.merge_price(trades, equity_data, time="09:29", column_name="intraday_open")

        trades.loc[:, "momentum_value"] = (trades.close - trades.intraday_open) / (
                trades.intraday_high - trades.intraday_low
        )

        trades = trades[trades.momentum_value > 0.6]
        trades = trades[trades.close > trades.close.rolling(10).mean()]

        trades.loc[:, "transaction_type"] = "BUY"
        trades.loc[:, 'tradingsymbol'] = trades.symbol
        trades.loc[:, "quantity"] = (50000/trades.close).astype(int)

        return trades
