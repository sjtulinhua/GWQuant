# encoding: UTF-8

"""

manage traders

"""
import logging
import garagequant.eventdriver as evtd
from garagequant.dataservice.oanda import oandafeed

logger = logging.getLogger(__name__)


class Trader:
    pass


class BackTrader(Trader):
    def __init__(self, brokerconfig, backtestconfig):
        self._broker_config = brokerconfig
        self._backtest_config = backtestconfig
        self._data_service = None
        self._event_driver = None

        self._init_backtrader()

    def run_backtest(self):
        data_feed = self._data_service.backtest_data_feed(self._backtest_config)


        while True:
            try:
                bar = next(data_feed)
                # print(bar)
            except StopIteration:
                logger.info(f'data feeding finished')
                break

    def _init_backtrader(self):
        self._event_driver = evtd.EventDriver()
        self._data_service = self._get_data_service()

    def _get_data_service(self):
        if self._backtest_config['broker'] == 'oanda':
            return oandafeed.OandaDataService(self._broker_config)