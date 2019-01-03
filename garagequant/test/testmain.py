# encoding: UTF-8

"""

Master test

"""

import yaml
import logging

import garagequant.eventdriver
from garagequant.dataservice.oanda import oandafeed

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


def test_yaml_load():
    with open('tradeconfig.yaml', 'r') as f:
        yamlconfig = yaml.load(f)
    return yamlconfig


if __name__ == '__main__':
    setup_logger()

    # eventdriver.test_event_driver()
    tradeconfig = test_yaml_load()

    if tradeconfig['action'] == 'getdata':
        if tradeconfig['getdata']['broker'] == 'oanda':
            oandafeed.fetch_oanda_data(tradeconfig['oanda'], tradeconfig['getdata'])

    elif tradeconfig['action'] == 'backtest':
        logger.info('to backtest something')
        pass

    elif tradeconfig['action'] == 'livetrade':
        logger.info('to livetrade')
        pass

    else:
        logger.error('wrong action type, check your tradeconfig file')
