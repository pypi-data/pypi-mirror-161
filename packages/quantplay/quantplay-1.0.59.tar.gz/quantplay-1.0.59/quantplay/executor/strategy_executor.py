import threading
# TODO: Import other broker classes
import traceback
from collections import defaultdict
from queue import Empty as empty_exception
from quantplay.utils.constant import Constants

from quantplay.brokerage.zerodha.ZBroker import ZBroker
from quantplay.brokerage.angelone.angel_broker import AngelBroker
from quantplay.exception.exceptions import (
    QuantplayOrderPlacementException,
    StrategyInvocationException,
)
from quantplay.utils.exchange import Market


class UserStrategiesExecutor:
    def __init__(self, broker_name, strategies):
        self.strategies = strategies

        for s in self.strategies:
            s.validate_production()
            s.add_derivative_symbols(mode='prod')

        required_tick_intervals = list(
            set([s.required_tick_interval() for s in self.strategies])
        )

        symbols_to_subscribe = defaultdict(set)
        for s in self.strategies:
            for (
                security_type,
                symbols,
            ) in s.stream_symbols_by_security_type.items():
                stream_symbols_from_exchange = Market.EXCHANGE_MAPPINGS[
                    s.exchange_to_trade_on
                ][security_type]
                symbols_to_subscribe[stream_symbols_from_exchange].update(symbols)

        self.broker = None
        if broker_name == "Zerodha":
            self.broker = ZBroker(required_tick_intervals, True)
        elif broker_name == "AngelOne":
            print(required_tick_intervals)
            self.broker = AngelBroker(required_tick_intervals, True)
        else:
            raise Exception(
                f"Broker {self.broker} not supported yet. Supported Brokers: Zerodha"
            )

        for exchange, symbols in symbols_to_subscribe.items():
            self.broker.add_strategy_symbols(list(symbols), exchange)

        Constants.logger.info(f"Strategies Instruments Subscribed: {self.broker.strategy_instruments}")

        self.broker.bootstrap_strategy_child_orders_map(self.strategies)

        load_data_for_days = max([s.data_required_for_days for s in self.strategies])

        Constants.logger.info(f"Loading Historical Data for {load_data_for_days} days")

        self.broker.load_historical_market_feed(load_data_for_days)

        Constants.logger.info(f"Historical data loaded")

    def run_strategies(self):
        while True:
            try:
                (
                    interval,
                    tick_time,
                ) = self.broker.processed_tick_interval_queue.get(timeout=5)
                Constants.logger.info("Processing {} {}".format(interval, tick_time))
                print("Processing {} {}".format(interval, tick_time))
                for strategy in self.strategies:
                    if strategy.should_exit(tick_time):
                        Constants.logger.info(
                            f"Closing child orders for strategy {strategy.strategy_tag}"
                        )
                        self.broker.close_child_orders(tag=strategy.strategy_tag)
                        Constants.logger.info(
                            f"Strategy {strategy.strategy_tag} child orders are modified to be executed immediately"
                        )

                    if strategy.should_invoke(interval, tick_time):
                        Constants.logger.info(f"Invoking Strategy {strategy}")
                        print(f"Invoking Strategy {strategy}")

                        market_data = self.broker.market_df(
                            strategy.required_tick_interval()
                        )

                        market_data = market_data[
                            market_data.security_type.isin(["OPT", "FUT"])
                            | market_data.symbol.isin(
                                strategy.stream_symbols_by_security_type["EQ"]
                            )
                        ]

                        try:
                            orders = strategy.live_orders(market_data, tick_time)
                        except StrategyInvocationException as e:
                            Constants.logger.info(
                                f"[STRATEGY_INVOCATION_FAILED] Failed to invoke {strategy.strategy_tag} got {e}"
                            )
                            traceback.print_exc()
                            continue

                        if not len(orders):
                            Constants.logger.info(
                                f"No orders to be executed for strategy {strategy.strategy_tag}"
                            )
                            continue



                        for order in orders:
                            Constants.logger.info("order [{}] by [{}]".format(strategy.strategy_tag, order))
                            # try:
                            #     order_id = self.broker.place_or_modify_order(
                            #         order, is_new_order=True
                            #     )
                            #     print(f"Executed Order {order} OrderId {order_id}")
                            # except QuantplayOrderPlacementException as e:
                            #     print(
                            #         f"[ORDER_PLACEMENT_FAILED] Failed to place {strategy.strategy_tag} order {order} got {e}"
                            #     )
                            #     traceback.print_exc()

                        Constants.logger.info(f"Finished executing strategy {strategy}")
            except empty_exception:
                Constants.logger.info("waiting for new tick addition to market dataframe")
                print("waiting for new tick addition to market dataframe")
                pass
            except Exception as e:
                Constants.logger.info(f"[CRITICAL_UNKNOWN_EXCEPTION] something went wrong {e}")
                traceback.print_exc()

    def start_execution(self):
        th = threading.Thread(target=self.run_strategies)
        th.start()
        self.broker.connect()


