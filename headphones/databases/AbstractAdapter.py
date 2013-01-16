import headphones

__author__ = 'aleksey'

class DBConnection(object):
    def __init__(self):
        if not headphones.CACHE_SIZEMB:
            #sqlite will work with this (very slowly)
            self.cache_size = 0
        else:
            self.cache_size = int(headphones.CACHE_SIZEMB)
        self.dbNiceName = 'abstract'

    def selectOne(self, sql, args=None):
        pass

    def selectOne(self, sql, args=None):
        sqlResults = self.action(sql, args).fetchone()
        if not sqlResults:
            return []

        return sqlResults

    def insert(self, sql, args=None):
        self.action(sql, args)

    def update(self, sql, args=None):
        self.action(sql, args)

    def delete(self, sql, args=None):
        self.action(sql, args)

    def action(self, sql, args=None):
        pass

    def selectSome(self, query, off, lim, args=None):
        pass

    def select(self, query, args=None):
        pass

    def upsert(self, tableName, valueDict, keyDict):
        pass

    def tableExport(self, tableName):
        pass

    def maintenance(self):
       pass

    def dbcheck(self):
        pass
