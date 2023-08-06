from quantplay.service import market

symbols = (
    market.symbols("NSE_INDICES")
    + market.symbols("NSE_ALL_STOCKS")
    + ["INDIA VIX"]
    + market.symbols("FNO_STOCKS")
)
symbols = list(set(symbols))


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


symbol_chunks = list(chunks(symbols, 500))

for symbols in symbol_chunks:

    interval = "day"
    market_data = market.data(
        symbols_by_security_type={"EQ": symbols},
        interval=interval,
    )
    market_data = market_data[market_data.date >= "2021-12-01 00:00:00"]
    market_data = market_data[market_data.date < "2022-01-01 00:00:00"]

    symbols = market_data.symbol.unique()

    for symbol in symbols:
        print("Saving data for {}".format(symbol))
        symbol_data = market_data[market_data.symbol == symbol][
            ["symbol", "date", "open", "high", "low", "close", "volume"]
        ]
        symbol_data.to_csv(
            "~/Documents/QuantplaySampleData/NSE_EQ/{}/{}.csv".format(interval, symbol),
            index=False,
        )
