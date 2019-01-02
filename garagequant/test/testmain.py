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
    oandafeed.test_oanda_data_fetch(tradeconfig)
