# encoding: UTF-8

"""

Test garage quant

"""


import logging

import eventdriver
import oanda_dataservice

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s-%(name)s-%(levelname)s: %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s <mod: %(name)s> : %(message)s')
logger = logging.getLogger('__main__')
logger.addHandler(logging.StreamHandler())


if __name__ == '__main__':
    # eventdriver.test_event_driver()
    oanda_dataservice.test_oanda_dataservice()
    pass
