from abc import ABCMeta, abstractmethod
import headphones

class DBConnectionInterface(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        if not headphones.CACHE_SIZEMB:
            #sqlite will work with this (very slowly)
            self.cache_size = 0
        else:
            self.cache_size = int(headphones.CACHE_SIZEMB)
        self.dbNiceName = 'abstract'

    @abstractmethod
    def selectOne(self, sql, args=None):
        pass

    @abstractmethod
    def insert(self, sql, args=None):
        pass

    @abstractmethod
    def update(self, sql, args=None):
        pass

    @abstractmethod
    def delete(self, sql, args=None):
        pass

    @abstractmethod
    def action(self, sql, args=None):
        pass

    @abstractmethod
    def selectSome(self, query, off, lim, args=None):
        pass

    @abstractmethod
    def select(self, query, args=None):
        pass

    @abstractmethod
    def upsert(self, tableName, valueDict, keyDict):
        pass

    @abstractmethod
    def tableExport(self, tableName):
        pass

    @abstractmethod
    def maintenance(self):
        pass

    @abstractmethod
    def dbcheck(self):
        pass
