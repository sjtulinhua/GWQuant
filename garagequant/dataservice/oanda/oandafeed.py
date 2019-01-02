# encoding: UTF-8

"""

Data service

"""

import time
import os
import h5py
import logging
import pandas as pd
#import numpy as np
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
    def __init__(self):
        self.param = {
            'price': Oanda.data_spec['price'],
            'from': Oanda.data_spec['startdate'],
            'to': Oanda.data_spec['enddate'],
            'count': Oanda.request_bar_cnt
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

    def backtest_data_feed(self):
        try:
            self._load_histdata()
        except Exception as e:
            logger.exception(f'load historical data error:\n{str(Exception)} - {str(e)}')

    def live_data_feed(self):
        pass

    def _load_histdata(self):
        """
        To read or download historical data sets defined by data_spec
        :return:
        """
        storage = Oanda.data_spec['storage']
        if storage == 'hdf5':
            self._load_hdf5()
            return

    def _create_client_session(self):
        self._oanda_client = API(access_token=Oanda.token, environment=Oanda.account_type)

    def _load_hdf5(self):
        """
        parse the list of target hdf5 files with fetch params from data_spec section of trade configuration
        """
        fetch_list = []

        # each hdf5 file accommodates on instrument, each period is stored in separate group
        for inst in Oanda.data_spec['instruments']:
            api_param_list = []
            file_path = os.path.expanduser(Oanda.storage_spec['hdf5']['file_path'])
            file_name = str.lower(f'{inst}_{Oanda.account_type}.hdf5')

            for granularity in Oanda.data_spec['periods']:
                param = OandaApiParam()
                param.set_param_field('granularity', granularity)
                api_param_list.append(param)

            fetch_list.append((file_path, file_name, inst, api_param_list))
        #
        # below is going to store each granularity into one separate h5 file
        #
        # for inst in Oanda.data_spec['instruments']:
        #     for granularity in Oanda.data_spec['periods']:
        #         file_path = os.path.expanduser(Oanda.storage_spec['hdf5']['file_path'])
        #         file_name = str.lower(f'{inst}_{granularity}_{Oanda.account_type}.hdf5')
        #         api_param['granularity'] = granularity
        #         fetch_list.append((file_path, file_name, inst, api_param))

        self._fetch_data_to_h5(fetch_list)

    def _fetch_data_to_h5(self, fetch_list):
        # create Oanda session
        self._create_client_session()

        # download and save to files
        for path, fname, inst, param_list in fetch_list:
            gqutil.check_data_dir(path)
            path_name = os.path.join(path, fname)

            # each hdf5 file accommodates on instrument, each period is stored in separate group
            with pd.HDFStore(path_name, 'a', complevel=HDF5_COMP_LEVEL, complib=HDF5_COMP_LIB) as h5f:
                # todo avid downloading existed data
                logger.info(f'download to file: {os.path.abspath(path_name)}')

                for param in param_list:

                    start_time = time.time()

                    # The factory returns a generator generating consecutive
                    # requests to retrieve full history from date 'from' till 'to'
                    api_param = param.param
                    for r in InstrumentsCandlesFactory(instrument=inst, params=api_param):
                        self._oanda_client.request(r)
                        candles = r.response.get('candles')  # candles is a list
                        if (candles == []):
                            logger.info(f'skip to write next: find empty data (with candles == [])')
                            continue
                        else:
                            logger.info(f'* download progress: {candles[0].get("time")}')

                        candles = list(map(self._normalize_raw_candles, candles))
                        df_candles = pd.DataFrame(candles)

                        # shift to appropriate data type for shrinking data size
                        for col in df_candles.columns:
                            df_candles[col] = df_candles[col].astype(Oanda.storage_spec['tableheader'][col], copy=True)
                            logger.debug(df_candles[col].dtypes)

                        # reset index
                        df_candles.set_index('timestamp', inplace=True)

                        # write to file
                        h5f.append(api_param['granularity'], df_candles)

                    end_time = time.time()
                    logger.info('\t - it took {} second to download {} - {} '
                                .format(end_time-start_time, inst, api_param['granularity']))

    def _normalize_raw_candles(self, candles):
        from collections import OrderedDict
        ohlc = OrderedDict(timestamp=pd.to_datetime(candles['time']),
                    openbid=float(candles['bid']['o']),
                    highbid=float(candles['bid']['h']),
                    lowbid=float(candles['bid']['l']),
                    closebid=float(candles['bid']['c']),
                    openask=float(candles['ask']['o']),
                    highask=float(candles['ask']['h']),
                    lowask=float(candles['ask']['l']),
                    closeask=float(candles['ask']['c']),
                    volume=float(candles['volume']),
                    complete=float(candles['complete']))

        return ohlc
# module test
def test_oanda_data_fetch(tradeconfig):
    ods = OandaDataService(tradeconfig['oanda'])
    ods.backtest_data_feed()
