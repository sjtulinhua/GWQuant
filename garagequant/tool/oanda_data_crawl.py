#!/usr/bin/python
import sys
import time
import getopt
from oandapyV20 import API
import json
import csv
import pymongo
import funcy as fy
import oandapyV20.endpoints.accounts as accounts
from oandapyV20.contrib.factories import InstrumentsCandlesFactory

from crawlerconfig import oanada_account_info, crawler_param_list


def client_session(token, account_type):
    if (account_type == 'live'):
        return API(access_token=token, environment='live')
    else:
        return API(access_token=token)

def get_symbol(client, account_id, select):
    r = accounts.AccountInstruments(accountID=account_id)
    ins = client.request(r)
    #return [item['name'] for item in ins['instruments'] if item['name'][:3] == select]
    return r

def get_account_details(client, account_id):
    r = accounts.AccountDetails(account_id)
    ret = client.request(r)
    return r, ret # ret is a dictionary


def convert_candle_list_2_csv(csv_file, candle_list, skip_header):
    w = csv.writer(csv_file)
    if not (skip_header):
        header = list(candle_list[0].keys())
        pos = header.index('mid')
        header[pos:pos] = candle_list[0]['mid'].keys()
        header.remove('mid')
        # print('add header to csv: {}'.format(header))
        w.writerow(header)

    for row in candle_list:
        lst = list(row.values())
        for ls in lst:
            if type(ls).__name__ == 'dict':
                pos = lst.index(ls)
                lst[pos:pos] = ls.values()
                lst.remove(ls)
        w.writerow(lst)

def save_2file(client, param, saveto, account_type):
    params = param['api_param']

    file_2_write = "../output/{}.{}.{}.{}.{}".format(
        param['instrument'],
        params['granularity'],
        params['from'][0:20].replace('-', ''),
        params['to'][0:20].replace('-', ''),
        account_type)
    if (saveto == 'csv'):
        file_2_write += '.csv'
    print('Write data to {}'.format(file_2_write))

    with open(file_2_write, "w") as OUT:
        cnt = 0
        # The factory returns a generator generating consecutive
        # requests to retrieve full history from date 'from' till 'to'
        for r in InstrumentsCandlesFactory(instrument=param['instrument'], params=params):
            client.request(r)

            # data type
            # r.response:
            # {'instrument': 'EUR_USD',
            #  'granularity': 'S5',
            #  'candles': [{'complete': True, 'volume': 1, 'time': '2018-01-01T22:00:00.000000000Z', 'mid': {'o': '1.20052', 'h': '1.20052', 'l': '1.20052', 'c': '1.20052'}}]
            # }
            candles = r.response.get('candles')  # candles is a list
            if (candles == []):
                print('skip to write next: find empty data (with candles == []), at ')
                continue
            else:
                print('\t - download progress: {}'.format(candles[0].get('time')))

            start_time = time.time()

            if (saveto == 'string'):
                OUT.write(json.dumps(candles, indent=2))
            elif (saveto == 'csv'):
                convert_candle_list_2_csv(OUT, candles, skip_header=cnt)
            cnt += 1

            end_time = time.time()
            print('\t - it took {} second to write to {} '.format(end_time - start_time, saveto))

def init_mongodb(dbname):
    from crawlerconfig import mongodb_config as dbcfg
    db_client = pymongo.MongoClient(host=dbcfg['host'], port=dbcfg['port'], connect=False)

    # create database
    database_name = dbcfg['database_prefix'] + dbname \
        if dbcfg['database_prefix'] is not None else dbname
    database_name = database_name + dbcfg['database_postfix'] \
        if dbcfg['database_postfix'] is not None else database_name

    db = db_client[database_name]
    return db

def normalize_raw_candles(candles):
    date = candles['time'].replace('T', ' ')[:19]
    ohlc = dict(date=date,
                timestamp=date[-8:],
                open=float(candles['mid']['o']),
                high=float(candles['mid']['h']),
                low=float(candles['mid']['l']),
                close=float(candles['mid']['c']),
                volume=float(candles['volume']),
                complete=float(candles['complete']))

    return ohlc

def drop_duplicates_func(collection_obj):
        """删除重复数据"""
        c = collection_obj.aggregate([{"$group":
                                       {"_id": {'date': '$date'},
                                        "count": {'$sum': 1},
                                           "dups": {'$addToSet': '$_id'}}},
                                      {'$match': {'count': {"$gt": 1}}}
                                      ], allowDiskUse=True
                                     )

        def get_duplicates():
            for i in c:
                for dup in i['dups'][1:]:
                    yield dup

        length = 0

        for i in get_duplicates():
            collection_obj.delete_one({'_id': i})
            length += 1

        return length

def save_2mgdb(client, param, db):
    collection = db[param['api_param']['granularity']]

    for r in InstrumentsCandlesFactory(instrument=param['instrument'], params=param['api_param']):
        client.request(r)

        # data type
        # r.response:
        # {'instrument': 'EUR_USD',
        #  'granularity': 'S5',
        #  'candles': [{'complete': True, 'volume': 1, 'time': '2018-01-01T22:00:00.000000000Z', 'mid': {'o': '1.20052', 'h': '1.20052', 'l': '1.20052', 'c': '1.20052'}}]
        # }
        candles = r.response.get('candles')  # candles is a list
        if (candles == []):
            print('\t * skip to write next: find empty data (with candles == [])')
            continue
        else:
            print('\t - download progress: {}'.format(candles[0].get('time')))

        # write to mongodb
        bar_list = fy.walk(normalize_raw_candles, candles)

        start_time = time.time()
        for bar in bar_list:
            collection.insert_one(bar)
        end_time = time.time()
        print('\t - it took {} second to write to mongodb '.format(end_time - start_time))

    length = drop_duplicates_func(collection)
    print(f'\t <<collection:{collection}>> has been drop {length} duplicates!')

def get_hist_candles_2storage(client, account_type, crawler_param = None):
    if (crawler_param == None):
        print("-------  Error: no crawler parameters input ")
        return

    db = None
    saveto = crawler_param['save_to']
    print(f'\nsave to: {saveto}')

    for granularity in crawler_param['period_list']:
        param = {
            "instrument": crawler_param['instrument'],
            "api_param": {
                    "from": crawler_param['start_date'],
                    "to": crawler_param['end_date'],
                    "granularity": granularity,
                    "count": crawler_param['bar_count']
                }
            }

        print(f'Start to download: {param["instrument"]} on {granularity}')

        if (saveto == 'mgdb'):
            if (db == None):
                db = init_mongodb(dbname=param['instrument'])
            save_2mgdb(client, param, db)
        else:
            save_2file(client, param, saveto, account_type)


def setup_account(account_type):
    print("Ready to download data from {} account".format(account_type))

    if (account_type == 'live'):
        token = oanada_account_info['r_access_token']
        id = oanada_account_info['r_accountID']
    elif (account_type == 'sim'):
        token = oanada_account_info['p_access_token']
        id = oanada_account_info['p_accountID']
    else:
        print('wrong account type')
        return 9

    return id, token

def main(argv=None):
    if argv is None:
        argv = sys.argv

    account_type = 'live'

    opts, args = getopt.getopt(argv[1:], "ha:", ["help", 'account'])
    for key, value in opts:
        if (key in ['-h', '--h']):
            print('here we need add help topics')
            return

        elif (key in ['-a', '--atype']):
            account_type = value
            print('account_type {}'.format(account_type))
            if (account_type not in ['live', 'sim']):
                print("wrong account type")
                return

    account_id, access_token = setup_account(account_type)
    print(f"account: {account_id}")
    print(f"token: {access_token}")

    client = client_session(access_token, account_type)

    #r = get_account_details(client, account_id)
    #r = get_symbol(client, account_id, 'EUR')
    #r = get_hist_candles_2frame(client, account_id, account_type, 'EUR_USD', 'M1', "2018-01-01T00:00:00Z", "2018-11-29T00:00:00Z", csv=True)

    for crawler_param in crawler_param_list:
        get_hist_candles_2storage(client, account_type, crawler_param)



# ref to https://www.cnblogs.com/LarryGen/p/5427102.html for how to write main function
if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print('At this time it takes : {} second to complete the download'.format(end_time - start_time))
