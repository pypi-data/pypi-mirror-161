from quantplay.brokerage.generics.broker import Broker
from smartapi import SmartConnect
from quantplay.config.qplay_config import QplayConfig
from quantplay.model.exchange.instrument import QuantplayInstrument
import pickle
from retrying import retry
import codecs
from datetime import timedelta, datetime
from quantplay.utils.constant import Constants
import pandas as pd
import numpy as np
import getpass
import traceback
from smartapi import SmartWebSocket
from quantplay.model.exchange.order import (
    QuantplayExchangeOrder,
    QuantplayExchangeResponseType,
    QuantplayExchangeResponse,
)
import requests
import json


class AngelBroker(Broker):
    angelone_api_key = "angelone_api_key"
    angelone_api_secret = "angelone_api_secret"
    angelone_client_id = "angelone_client_id"
    angelone_wrapper = "angelone_wrapper"
    angel_refresh_token = "angel_refresh_token"

    def __init__(self, tick_intervals, live_trade):
        try:
            wrapper = QplayConfig.get_value(AngelBroker.angelone_wrapper)
            self.wrapper = pickle.loads(codecs.decode(wrapper.encode(), "base64"))
            self.refreshToken = QplayConfig.get_value(AngelBroker.angel_refresh_token)
            user_profile_response = self.wrapper.getProfile(self.refreshToken)
            if user_profile_response['message'] != "SUCCESS":
                raise Exception("AngelOne Token Expired")
            else:
                print(user_profile_response)
        except Exception as e:
            Constants.logger.error(e)
            self.wrapper = self.generate_token()
            print(self.wrapper.getProfile(self.refreshToken))
        self.refreshToken = QplayConfig.get_value(AngelBroker.angel_refresh_token)
        self.client_id = QplayConfig.get_value(AngelBroker.angelone_client_id)

        self.angelone_ws = SmartWebSocket(self.wrapper.getfeedToken(), self.client_id)
        super(AngelBroker, self).__init__(tick_intervals, live_trade)
        self.populate_instruments()

    def get_all_child_orders(self):
        orders_data = self.wrapper.orderBook()['data']
        if orders_data == None:
            return []
        trigger_orders = [
            QuantplayExchangeOrder.from_zerodha_order(data, is_child_order=True)
            for data in orders_data
            if data["status"] == "TRIGGER PENDING" and "tag" in data
        ]
        return trigger_orders

    @retry(
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        stop_max_attempt_number=8,
    )
    def get_historical_data_from_angelone(self, instrument, start_date, end_date, interval):
        return self.wrapper.getCandleData({
            "exchange": "NSE",
            "symboltoken": instrument,
            "interval": interval,
            "fromdate": start_date,
            "todate": end_date
        })['data']

    def get_historical_data(self, instrument, start_date, end_date):
        data_by_interval = dict()

        interval_map = {
            "minute": "ONE_MINUTE"
        }
        for interval in self.tick_intervals:
            if interval == "5minute":
                days_diff = 100
            elif interval == "minute":
                days_diff = 60
            elif interval == "day":
                days_diff = 2000
            else:
                raise Exception("interval {} not whitelisted".format(interval))

            time_diff = timedelta(days=days_diff)

            data = []
            while end_date > (start_date + time_diff):
                Constants.logger.info(
                    "querying data from [%s] [%s], symbol [%s] interval [%s]"
                    % (start_date, start_date + time_diff, self.instrument_id_to_symbol_map[instrument], interval)
                )
                temp_data = self.get_historical_data_from_angelone(instrument,
                                                                   start_date.strftime('%Y-%m-%d %H:%M'),
                                                                   (start_date + time_diff).strftime('%Y-%m-%d %H:%M'),
                                                                   interval_map[interval])

                start_date += time_diff

                if temp_data is not None and len(temp_data) > 0:
                    data = data + temp_data

            Constants.logger.info(
                "querying data from [%s] [%s] symbol [%s] interval [%s]"
                % (start_date, end_date, self.instrument_id_to_symbol_map[instrument], interval)
            )
            temp_data = self.get_historical_data_from_angelone(instrument,
                                                               start_date.strftime('%Y-%m-%d %H:%M'),
                                                               end_date.strftime('%Y-%m-%d %H:%M'),
                                                               interval_map[interval])
            data = data + temp_data
            Constants.logger.info("Interval {} Total size {}".format(interval, len(data)))

            df = pd.DataFrame(data)
            df.rename(columns={0: 'date', 1: 'open', 2: 'high', 3:'low', 4:'close', 5: 'volume'}, inplace=True)

            if len(df) > 0:
                symbol = self.instrument_id_to_symbol_map[instrument]
                df.loc[:, "symbol"] = symbol
                df.loc[:, 'date'] = pd.to_datetime(df.date)
                df.loc[:, "date"] = df["date"].dt.tz_localize(None)
                df.loc[:, "date"] = pd.to_datetime(df.date)
                df.to_csv('/tmp/angelone_df.csv')

            data_by_interval[interval] = df

        return data_by_interval

    def populate_instruments(self):
        data = requests.get("https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json")
        inst_data = json.loads(data.content)
        inst_data = pd.DataFrame(inst_data)
        inst_data.loc[:, 'exchange'] = inst_data.exch_seg
        inst_data = inst_data[inst_data.exchange.isin(["NSE", "NFO"])]
        inst_data.loc[:, 'instrument_token'] = inst_data.token.astype(int)
        inst_data.loc[:, 'symbol'] = inst_data['symbol'].str.replace('-EQ','')

        assert set(['OPTSTK', 'OPTIDX', 'FUTSTK', 'FUTIDX']) == set(inst_data[inst_data.exch_seg == "NFO"].instrumenttype.unique())

        inst_data.loc[:, 'segment'] = None
        inst_data.loc[:, 'segment'] = np.where((inst_data.exch_seg == "NFO") & (
                    (inst_data.instrumenttype == "OPTIDX") | (inst_data.instrumenttype == "OPTSTK")),
                                               "NFO-OPT", inst_data.segment)
        inst_data.loc[:, 'segment'] = np.where((inst_data.exch_seg == "NFO") & (
                    (inst_data.instrumenttype == "FUTIDX") | (inst_data.instrumenttype == "FUTSTK")),
                                               "NFO-FUT", inst_data.segment)
        inst_data.loc[:, 'segment'] = np.where(inst_data.exch_seg == "NSE",
                                               "NSE", inst_data.segment)
        inst_data = inst_data[~inst_data.segment.isna()]
        inst_data.loc[:, 'instrument_type'] = np.where(inst_data.segment == "NFO-FUT", "FUT", None)
        inst_data.loc[:, 'instrument_type'] = np.where(inst_data.segment == "NSE", "EQ",
                                                       inst_data.instrument_type)
        inst_data.loc[:, 'instrument_type'] = np.where(
            ((inst_data.segment == "NFO-OPT") & (inst_data.symbol.str[-2:] == "PE")),
            "PE", inst_data.instrument_type)
        inst_data.loc[:, 'instrument_type'] = np.where(
            ((inst_data.segment == "NFO-OPT") & (inst_data.symbol.str[-2:] == "CE")),
            "CE", inst_data.instrument_type)
        inst_data = inst_data.to_dict('records')

        instruments = list(
            map(
                lambda z_instrument: QuantplayInstrument.from_angelone_instrument(
                    z_instrument
                ),
                inst_data,
            )
        )

        Broker.populate_instruments(self, instruments)

    def connect(self):
        self.angelone_ws.connect()

    def initiate_live_trade_callbacks(self):
        self.angelone_ws._on_open = self.on_open
        self.angelone_ws._on_message = self.on_message
        self.angelone_ws._on_error = self.on_error
        self.angelone_ws._on_close = self.on_close

    def on_message(self, ws, message):
        print("Ticks: {}".format(message))

    def on_open(self, ws):
        print("on open")
        stream_data = "&".join(["nse_cm|{}".format(str(x)) for x in self.streaming_instruments])
        self.angelone_ws.subscribe("mw", stream_data)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("Close")


    def add_strategy_symbols(self, symbols, exchange):
        super(AngelBroker, self).add_strategy_symbols(symbols, exchange)
        if self.live_trade:
            Constants.logger.info("assigning callbacks")
            self.initiate_live_trade_callbacks()

    def configure(self):
        quantplay_config = QplayConfig.get_config()

        print("Enter AngelOne API key:")
        api_key = input()

        print("Enter AngelOne API Secret:")
        api_secret = input()

        print("Enter AngelOne Client ID:")
        client_id = input()

        quantplay_config['DEFAULT'][AngelBroker.angelone_api_key] = api_key
        quantplay_config['DEFAULT'][AngelBroker.angelone_api_secret] = api_secret
        quantplay_config['DEFAULT'][AngelBroker.angelone_client_id] = client_id

        with open('{}/config'.format(QplayConfig.config_path), 'w') as configfile:
            quantplay_config.write(configfile)

    def validate_config(self, quantplay_config):
        if quantplay_config is None:
            return False
        if AngelBroker.angelone_api_key not in quantplay_config['DEFAULT']:
            return False
        if AngelBroker.angelone_api_secret not in quantplay_config["DEFAULT"]:
            return False
        if AngelBroker.angelone_client_id not in quantplay_config["DEFAULT"]:
            return False

        return True

    def generate_token(self):
        quantplay_config = QplayConfig.get_config()

        if not self.validate_config(quantplay_config):
            self.configure()
            quantplay_config = QplayConfig.get_config()
        api_key = quantplay_config['DEFAULT'][AngelBroker.angelone_api_key]
        api_secret = quantplay_config['DEFAULT'][AngelBroker.angelone_api_secret]
        client_id = quantplay_config['DEFAULT'][AngelBroker.angelone_client_id]
        wrapper = SmartConnect(api_key=api_key)

        password = getpass.getpass()
        data = wrapper.generateSession(client_id, password)
        self.refreshToken = data['data']['refreshToken']
        QplayConfig.save_config(AngelBroker.angel_refresh_token, self.refreshToken)

        QplayConfig.save_config("angelone_wrapper", codecs.encode(pickle.dumps(wrapper), "base64").decode())
        return wrapper