# encoding: UTF-8

"""

Data service

"""

from abc import ABC, abstractmethod


class DataService(ABC):
    @abstractmethod
    def backtest_data_feed(self, config):
        pass
