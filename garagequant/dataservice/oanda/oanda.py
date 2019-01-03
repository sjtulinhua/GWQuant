# encoding: UTF-8

"""

Oanda common info

"""


class Oanda:
    id = None
    token = None
    account_type = None

    @staticmethod
    def oanda_initialize(oanda_config):
        Oanda.id = oanda_config['account']['id']
        Oanda.token = oanda_config['account']['token']
        Oanda.account_type = oanda_config['account']['type']

