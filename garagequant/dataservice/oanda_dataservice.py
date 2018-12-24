# encoding: UTF-8

"""

Data service

"""

# OANDA api imports
from oandapyV20 import API

import logging
logger = logging.getLogger(__name__)

class OanadaDataService:
    def __init__(self):
        self._id = ''
        self._token = ''
        self._data_spec = {}
        pass

    def set_query_param(self, storage, data_spec):
        """
        add historical data reference to data service
        :param storage: storage type, support 'hdf5', 'csv', 'mongodb', 'plain'
        :param data_spec: specify instruments, periods, etc.
        :return:
        """
        pass

    def data_feed(self):
        pass

    def create_client_session(self):
        return API(access_token=self._token, environment='live')

# module test
def test_oanda_dataservice():
    ods = OanadaDataService()
    ods.create_client_session()
