# encoding: UTF-8

"""

Data service

"""

import time
import os
import logging
# import datetime
import contextlib
import pandas as pd
# import numpy as np
# import tables as tb

# import oanda api
from oandapyV20 import API
from oandapyV20.contrib.factories import InstrumentsCandlesFactory

# import in-house modules
from .oanda import Oanda
from garagequant.utils import gqutil

""" HDF5_COMP_LEVEL：0~9 """
HDF5_COMP_LEVEL = 4
""" HDF5_COMP_LIB: 'blosc', 'bzip2', 'lzo', 'zlib'"""
HDF5_COMP_LIB = 'blosc'

logger = logging.getLogger(__name__)


class OandaApiParam:
    def __init__(self, data_spec):
        self.param = {
            'price': data_spec['price'],
            'from': data_spec['startdate'],
            'to': data_spec['enddate']
        }

    def set_param_field(self, field, value):
        self.param[field] = value


class OandaDataService:

    def __init__(self, oanda_config=None):
        try:
            Oanda.oanda_initialize(oanda_config)
        except Exception as e:
            logger.exception(f'OandaDataService instance init error:\n{str(Exception)} - {str(e)}')

        self._oanda_client = None
        self._fetch_stats = []

    def backtest_data_feed(self):
        pass

    def live_data_feed(self):
        pass

    def fetch_data(self, fetch_config):
        """
        download data from oanda server following data_config rules
        """
        try:
            storage = fetch_config['storage']
            if storage == 'hdf5':
                self._fetch_to_hdf5(fetch_config['storage_spec'], fetch_config['data_spec'])

        except Exception as e:
            logger.exception(f'load historical data error:\n{str(Exception)} - {str(e)}')

        #
        # dump download stats
        #
        if self._fetch_stats:
            for fetch_stats_dict in self._fetch_stats:
                for file_name, group_list in fetch_stats_dict.items():
                    logger.info(str(file_name))
                    for stats_dict in group_list:
                        for key, val in stats_dict.items():
                            if key == 'request count' or key == 'download time':
                                logger.info(f'\t\t{key}: {val}')
                            else:
                                logger.info(f'\t{key}: {val}')

    def _fetch_to_hdf5(self, storage_spec, data_spec):
        """
        parse the list of target hdf5 files with fetch params from data_spec section of trade configuration
        """
        fetch_list = []

        # each hdf5 file accommodates on instrument, each period is stored in separate group
        for inst in data_spec['instruments']:
            api_param_list = []

            # ensure the data directory exists
            file_path = os.path.expanduser(storage_spec['hdf5']['file_path'])
            if not os.path.isdir(file_path):
                gqutil.check_data_dir(file_path)

            file_name = str.lower(f'{inst}_{Oanda.account_type}.hdf5')
            path_name = os.path.join(file_path, file_name)

            for granularity in data_spec['periods']:
                api_param = OandaApiParam(data_spec)
                api_param.set_param_field('granularity', granularity)
                api_param_list.append(api_param)

            fetch_list.append((path_name, inst, api_param_list))

        self._download_data_to_hdf5(fetch_list, storage_spec['tableheader'])

    def _download_data_to_hdf5(self, download_list, field_dtype_dict):
        # create Oanda session
        if self._oanda_client is None:
            self._create_client_session()

        # download and save to files
        for path_name, inst, param_list in download_list:

            # each hdf5 file accommodates on instrument, each period is stored in separate group
            with contextlib.closing(
                    pd.HDFStore(path_name, 'a', complevel=HDF5_COMP_LEVEL, complib=HDF5_COMP_LIB)) as h5f:

                # todo avid downloading existed data:
                #       1. label existed data by unique key which combining volume and start/to dates
                #       2. could assume already existed data is correct (continuously, no missed data in it)
                #       3. add unique key as an attr of a h5 table so that can used for judge new data
                #          whether already existed or not

                logger.info(f'download to file: {os.path.abspath(path_name)}')

                stats = {f'{path_name}': [], }
                child_stats = stats[f'{path_name}']

                for api_param in param_list:
                    start_time = time.time()

                    requests = 0
                    stats_dict = {}

                    # The factory returns a generator generating consecutive
                    # requests to retrieve full history from date 'from' till 'to'
                    for r in InstrumentsCandlesFactory(instrument=inst, params=api_param.param):
                        self._oanda_client.request(r)
                        candles = r.response.get('candles')  # candles is a list
                        requests += 1

                        if not candles:
                            logger.info(f'skip to write next: find empty data with candles == []')
                            continue

                        else:
                            logger.info(f'* download progress: {candles[0].get("time")}')

                        candles = list(map(self._normalize_oanda_raw_candles, candles))
                        df_candles = pd.DataFrame(candles)

                        # shift to appropriate data type for shrinking data size
                        for col in df_candles.columns:
                            df_candles[col] = df_candles[col].astype(field_dtype_dict[col], copy=True)
                            logger.debug(df_candles[col].dtypes)

                        # reset index
                        # df_candles.set_index('timestamp', inplace=True)

                        # write to file
                        h5f.append(api_param.param['granularity'], df_candles)

                    end_time = time.time()

                    stats_dict['group'] = api_param.param['granularity']
                    stats_dict['request count'] = requests
                    stats_dict['download time'] = end_time - start_time
                    # logger.info('\t - it took {} second to download {} - {} '
                    #                .format(stats_dict['download time'], inst, stats_dict['group']))
                    child_stats.append(stats_dict)

                self._fetch_stats.append(stats)

    @staticmethod
    def _normalize_oanda_raw_candles(oanda_candles):
        from collections import OrderedDict
        ohlc = OrderedDict(timestamp=pd.to_datetime(oanda_candles['time']),
                           openbid=float(oanda_candles['bid']['o']),
                           highbid=float(oanda_candles['bid']['h']),
                           lowbid=float(oanda_candles['bid']['l']),
                           closebid=float(oanda_candles['bid']['c']),
                           openask=float(oanda_candles['ask']['o']),
                           highask=float(oanda_candles['ask']['h']),
                           lowask=float(oanda_candles['ask']['l']),
                           closeask=float(oanda_candles['ask']['c']),
                           volume=float(oanda_candles['volume']),
                           complete=float(oanda_candles['complete']))
        return ohlc

    def _create_client_session(self):
        self._oanda_client = API(access_token=Oanda.token, environment=Oanda.account_type)


def fetch_oanda_data(oandaconfig, fetchconfig):
    """
    for action == getdata, download data from oanda server
    #todo for simplifying, data would be override, improve this!
    """
    ods = OandaDataService(oandaconfig)
    ods.fetch_data(fetchconfig)


def feed_oanda_data(tradeconfig):
    # backtest data setup
    # start_date = datetime.datetime(2015, 1, 1)
    # end_date = datetime.datetime(2018, 1, 1)
    # instrument = 'EUR_USD'
    # granularity = 'D'
    # backtest_data_feed(instrument, granularity, start_date, end_date)
    pass
