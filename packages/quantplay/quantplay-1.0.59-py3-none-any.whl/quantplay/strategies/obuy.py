
from quantplay.utils.constant import TickInterval
from quantplay.strategy.base import QuantplayAlgorithm
from quantplay.service import market
from quantplay.order_execution.mean_price import MeanPriceExecutionAlgo
import numpy as np
import pandas as pd


class OBuy(QuantplayAlgorithm):
    def __init__(self):

        # Mandatory Attributes
        self.interval = TickInterval.minute
        self.entry_time = "^13:(4[5-9]|5[0-9]):00$"
        self.exit_time = "9:25"
        self.strategy_trigger_times = [self.entry_time]
        self.exchange_to_trade_on = "NFO"
        self.option_nearest_expiry_offset = 0
        self.stream_symbols_by_security_type = {
            "EQ": ["NIFTY 50", "NIFTY BANK", "INDIA VIX"]
        }
        self.columns_for_uuid = ["date", "symbol"]
        self.exact_number_of_orders_per_uuid = 1
        self.strategy_type = "overnight"
        self.strategy_tag = "obuy"
        self.option_chain_depth = 8
        self.holding_days = 1
        self.backtest_after_date = "2021-06-01"
        self.backtest_before_date = "2022-02-25"
        self.execution_algo = MeanPriceExecutionAlgo(7)

        # Optional Attribute
        self.data_required_for_days = 20

        super(OBuy, self).__init__()

    def validate_input(self, equity_data):
        unique_equity_symbols = list(equity_data.symbol.unique())
        assert len(unique_equity_symbols) == len(
            self.stream_symbols_by_security_type["EQ"]
        )
        assert set(unique_equity_symbols) == set(
            self.stream_symbols_by_security_type["EQ"]
        )



    def add_rvi_signal_score(self, trades):
        trades.loc[:, "rvi"] = (trades.close - trades.intraday_open) / (
            trades.intraday_high - trades.intraday_low
        )
        trades.loc[:, "signal_score"] = np.where(
            trades.rvi > 0.2, trades.signal_score + 1, trades.signal_score
        )

    def get_trades(self, market_data):
        market_data.loc[:, "date_only"] = pd.to_datetime(market_data.date.dt.date)
        market_data.loc[:, "day_of_week"] = market_data.date.dt.day_name()
        equity_data = market_data[market_data.security_type == "EQ"]
        self.validate_input(equity_data)

        equity_data = equity_data[equity_data.symbol.isin(["NIFTY 50", "NIFTY BANK"])]

        equity_data.loc[:, "sma"] = equity_data.close.rolling(300).mean()

        market.add_intraday_metrics(equity_data, "09:29", "14:00")
        trades = market.get_trades(equity_data, self.entry_time)

        trades = market.merge_price(
            trades, equity_data, time="09:29", column_name="intraday_open"
        )

        trades.loc[:, "signal_score"] = 0
        self.add_rvi_signal_score(trades)

        trades = trades[trades.signal_score >= 1]

        trades = trades.groupby(["symbol", "date_only"]).first().reset_index()
        trades = trades[trades.close > trades.close.rolling(10).mean()]

        trades = self.add_expiry(trades, security_type="OPT")
        trades = trades[trades.day_of_week.isin(["Monday", "Tuesday", "Friday"])]
        trades.loc[:, "itm_price"] = (round((trades.close * 0.985)/ trades.strike_gap)* trades.strike_gap)

        trades.loc[:, "itm_price"] = trades.itm_price.astype(int)

        ce_trades = market.option_symbol(
            trades, price_column="itm_price", option_type="CE"
        )

        trades = ce_trades

        trades.loc[:, "transaction_type"] = "BUY"
        trades.loc[:, "quantity"] = np.where(
            trades.symbol == "NIFTY 50",
            100,
            50,
        )

        trades = self.filter_uuids_not_matching_count(trades)

        return trades


if __name__ == "__main__":
    a, b = OBuy().backtest()
    print(a)
