import numpy as np
import pandas as pd
from quantplay.order_execution.mean_price import MeanPriceExecutionAlgo
from quantplay.service import market
from quantplay.strategy.base import QuantplayAlgorithm

class Nexon(QuantplayAlgorithm):
    def __init__(self):
        # Mandatory Attributes
        self.interval = "minute"
        self.entry_time = "14:(3[0-9]|4[0-9]|5[0-9])"
        self.exit_time = "9:15"
        self.strategy_trigger_times = ["14:(3[0-9]|4[0-9]|5[0-9])", "15:.."]
        self.exchange_to_trade_on = "NFO"
        self.future_nearest_expiry_offset = 1
        self.stream_symbols_by_security_type = {
            "EQ": ["NIFTY BANK"]
        }
        self.strategy_type = "overnight"
        self.strategy_tag = "nexon"
        self.holding_days = 1
        self.data_required_for_days = 20
        self.execution_algo = MeanPriceExecutionAlgo(7)

        super(Nexon, self).__init__()

    def get_trades(self, market_data):
        market_data.loc[:, "date_only"] = pd.to_datetime(market_data.date.dt.date)
        market_data = market_data[market_data.security_type == "EQ"]

        market_data.loc[:, 'intraday_high'] = market_data.close
        market_data.loc[:, 'intraday_high'] = np.where(
            (market_data.date.dt.hour == 9) | (market_data.date.dt.hour > 15),
            np.nan,
            market_data.intraday_high)
        market_data.loc[:, "intraday_high"] = market_data.groupby(
            ["symbol", "date_only"]
        ).intraday_high.cummax()

        trades = market_data[market_data.intraday_high == market_data.close]
        trades = trades[(trades.date.dt.hour > 14) | ((trades.date.dt.hour == 14) & (trades.date.dt.minute > 30))]

        trades = trades.groupby(["symbol", "date_only"]).first().reset_index()
        trades = self.add_expiry(trades, security_type="FUT")
        trades = market.future_symbol(trades)

        trades.loc[:, "transaction_type"] = "BUY"
        trades.loc[:, "quantity"] = 25

        return trades

