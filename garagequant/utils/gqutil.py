# encoding: UTF-8

"""

private utils

"""
import os
import timeit
import logging
from threading import currentThread

logger = logging.getLogger(name=__name__)

def gq_hosting_thread_info(snippet):
    debug_trace('\n* ' + snippet + 'revent loop (__run_loop) in thread:')
    debug_trace('\t - ' + currentThread().name)
    debug_trace('\t - ' + str(currentThread().ident) + '\n')


def debug_trace(strings):
    print(strings)
    # pass

def check_data_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def measuretime(func):
    def measure(*args, **kwargs):
        t0 = timeit.default_timer()
        result = func(*args, **kwargs)
        elapsed = timeit.default_timer() - t0
        logger.info(f'[PFM] {func.__module__} -> {func.__name__} has consumed: {elapsed: {5}.{8}} sec. ')
        return result
    return measure