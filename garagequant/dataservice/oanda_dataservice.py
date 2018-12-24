# encoding: UTF-8

"""

Data service

"""

# OANDA api imports
from oandapyV20 import API

# Account configs
from accountinfo import garage_accounts


class OanadaDataService:
    def __init__(self):
        self._id = garage_accounts['Oanda']['id']
        self._token = garage_accounts['Oanda']['token']
        self._data_spec = {}
        pass

    def set_data_param(self, storage, data_spec):
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


if __name__ == '__main__':
    ods = OanadaDataService()
    ods.create_client_session()
