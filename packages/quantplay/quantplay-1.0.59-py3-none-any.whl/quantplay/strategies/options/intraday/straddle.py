from quantplay.strategy.base import QuantplayAlgorithm
from quantplay.utils.constant import TickInterval
from quantplay.service import market
import pandas as pd


class Straddle(QuantplayAlgorithm):
    def __init__(self):
        self.interval = TickInterval.minute
        self.entry_time = "09:29"
        self.exit_time = "15:15"
        self.strategy_trigger_times = [self.entry_time]
        self.exchange_to_trade_on = "NFO"
        self.option_nearest_expiry_offset = 0
        self.option_chain_depth = 0
        self.backtest_after_date = "2020-01-01"
        self.backtest_before_date = "2022-02-25"
        self.stream_symbols_by_security_type = {"EQ": ["NIFTY 50"]}
        self.strategy_type = "intraday"
        self.strategy_tag = "straddle"

        super(Straddle, self).__init__()

    def get_trades(self, market_data):
        equity_data = market_data[market_data.security_type == "EQ"]

        trades = market.get_trades(equity_data, entry_time_regex=self.entry_time)

        trades = self.add_expiry(trades, security_type="OPT")

        trades.loc[:, "atm_price"] = (
            round((trades.close / trades.strike_gap).astype(float)) * trades.strike_gap
        )
        trades.loc[:, "atm_price"] = trades.atm_price.astype(int)

        pe_trades = market.option_symbol(
            trades, price_column="atm_price", option_type="PE"
        )
        ce_trades = market.option_symbol(
            trades, price_column="atm_price", option_type="CE"
        )

        trades = pd.concat([pe_trades, ce_trades], axis=0)

        trades.loc[:, "transaction_type"] = "SELL"
        trades.loc[:, "stoploss"] = 0.5
        trades.loc[:, "quantity"] = 100

        return trades
