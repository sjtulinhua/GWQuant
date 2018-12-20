from oandakey import r_access_token
from oandakey import r_accountID
from oandakey import p_access_token
from oandakey import p_accountID

mongodb_config = {
    'host': 'localhost',
    'port': 27017,
    'database_prefix': 'GW_',
    'database_postfix': '_Oanda'
}

oanada_account_info = {
    'r_access_token': r_access_token,
    'r_accountID': r_accountID,
    'p_access_token': p_access_token,
    'p_accountID': p_accountID,
}

# one param dict for one instrument
crawler_param_list = [
    {
        'instrument': 'EUR_USD',
        'period_list': ['S5', 'S15', 'S30', 'M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D', 'W', 'M'],
        'start_date': '2018-11-01T00:00:00Z',
        'end_date': '2018-12-07T00:00:00Z',
        'save_to': 'mgdb',
        'bar_count': 2500
    },
    # {
    #     'instrument': 'EUR_USD',
    #     'period_list': ['M30'],
    #     'start_date': '2018-01-03T00:00:00Z',
    #     'end_date': '2018-01-08T00:00:00Z',
    #     'save_to': 'mgdb',
    #     'bar_count': 2500
    # }
]