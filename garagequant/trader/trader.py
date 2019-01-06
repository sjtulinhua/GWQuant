# encoding: UTF-8

"""

manage traders

"""
import logging
from garagequant.eventtype import *
from garagequant.eventdriver import Event
from garagequant.eventdriver import EventDriver
from garagequant.dataservice.oanda import oandafeed

logger = logging.getLogger(__name__)


class Trader:
    """
    Trader base class
    """
    pass


class BackTrader(Trader):
    def __init__(self, brokerconfig, backtestconfig):
        self._broker_config = brokerconfig
        self._backtest_config = backtestconfig
        self._data_service = None
        self._event_driver = None
        self._data_feed = None

        self._init_backtrader()

    def run_backtest(self):
        #
        # initialize backtest
        #
        self._data_feed = self._data_service.get_backtest_data_feed(self._backtest_config)

        # register events
        self._event_driver.register(EVENT_EMPTY_QUEUE, self._cb_empty_queue)
        self._event_driver.register(EVENT_DATA_FEED_BEGIN, self._cb_feed_begin)
        self._event_driver.register(EVENT_NEXT_BAR, self._cb_next_bar)
        self._event_driver.register(EVENT_DATA_FEED_END, self._cb_feed_end)
        self._event_driver.register(EVENT_STOP_LOOP, self._cb_stop_loop)

        # start event engin
        self._event_driver.start()
        self._event_driver.put_event(Event(EVENT_DATA_FEED_BEGIN, self._data_feed))

        # data_feed = self._data_service.get_backtest_data_feed(self._backtest_config)
        # while True:
        #     try:
        #         bar = next(data_feed)
        #         import pandas as pd
        #         logger.debug(f'{bar[1]["timestamp"]}')
        #     except StopIteration:
        #         logger.info(f'data feeding finished')
        #         break

    def _init_backtrader(self):
        self._event_driver = EventDriver()
        self._data_service = self._get_data_service()

    def _get_data_service(self):
        if self._backtest_config['broker'] == 'oanda':
            return oandafeed.OandaDataService(self._broker_config)

    def _cb_feed_begin(self, event_data):
        self._cb_next_bar(event_data)

    def _cb_feed_end(self, event_data):
        # todo : this is just codes for debug
        self._event_driver.put_event(Event(EVENT_STOP_LOOP))
        pass

    def _cb_next_bar(self, event_data):
        feed = event_data

        try:
            bar = next(feed)
            logger.debug(f'{bar[1]["timestamp"]}')
        except StopIteration:
            logger.info(f'data feeding finished')

            # todo Finish backtesting
            self._event_driver.put_event(Event(EVENT_DATA_FEED_END))
        else:
            self._event_driver.put_event(Event(EVENT_NEW_BAR, bar))

    def _cb_empty_queue(self, event_data):
        self._event_driver.put_event(Event(EVENT_NEXT_BAR, self._data_feed))

    def _cb_stop_loop(self, event_data):
        self._event_driver.stop()
        print('here')
