# encoding: UTF-8

'''

private utils

'''

from threading import currentThread

def gq_hosting_thread_info(snippet):
    print('\n* ' + snippet + 'revent loop (__run_loop) in thread:')
    print('\t - ' + currentThread().name)
    print('\t - ' + str(currentThread().ident) + '\n')