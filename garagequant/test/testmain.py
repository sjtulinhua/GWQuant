# encoding: UTF-8

"""

Master test

"""

import yaml
import logging

import eventdriver
import oanda_dataservice
logger = None

def setup_logger():
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s-%(name)s-%(levelname)s: %(message)s')
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t<mod: %(name)s> : %(message)s')
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
    test_yaml_load()
    oanda_dataservice.test_oanda_dataservice()

    pass
