# encoding: UTF-8

"""

Master tester

"""

import yaml
import logging

from garagequant.dataservice.oanda import oandafeed

import garagequant.eventdriver as evtd

logger = None


def setup_logger():
    # disable logging.info for 3rd party modules
    logging.getLogger('oandapyV20').setLevel(logging.WARNING)

    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s-%(name)s-%(levelname)s: %(message)s')
    # logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t<mod: %(name)s> : %(message)s')
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: \t%(message)s')
    global logger
    logger = logging.getLogger('__main__')
    logger.addHandler(logging.StreamHandler())


def test_yaml_load(config_file):
    with open(config_file, 'r') as f:
        yamlconfig = yaml.load(f)
    return yamlconfig


def run_backtesting(config_file):
    # initial a backtest
    ed = evtd.EventDriver()
    oandafeed.feed_oanda_data(tradeconfig)

if __name__ == '__main__':
    setup_logger()

    tradeconfig = test_yaml_load('tradeconfig.yaml')

    if tradeconfig['action'] == 'getdata':
        if tradeconfig['getdata']['broker'] == 'oanda':
            oandafeed.fetch_oanda_data(tradeconfig['oanda'], tradeconfig['getdata'])

    elif tradeconfig['action'] == 'backtest':
        if tradeconfig['getdata']['broker'] == 'oanda':
            run_backtesting(tradeconfig)
        pass

    elif tradeconfig['action'] == 'livetrade':
        logger.info('to livetrade')
        pass

    else:
        logger.error('wrong action type, check your tradeconfig file')
