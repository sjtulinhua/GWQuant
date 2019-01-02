# encoding: UTF-8

"""

Oanda common info

"""


class Oanda:
    id = None
    token = None
    account_type = None
    data_spec = None
    storage_spec = None
    request_bar_cnt = None

    @staticmethod
    def oanda_initialize(oanda_config):
        Oanda.id = oanda_config['account']['id']
        Oanda.token = oanda_config['account']['token']
        Oanda.account_type = oanda_config['account']['type']
        Oanda.data_spec = oanda_config['data_spec']
        Oanda.storage_spec = oanda_config['storage_spec']
        Oanda.request_bar_cnt = 2500

