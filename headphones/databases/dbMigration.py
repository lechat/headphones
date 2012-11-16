#  This file is part of Headphones.
#
#  Headphones is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Headphones is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Headphones.  If not, see <http://www.gnu.org/licenses/>.

import threading
from headphones.databases import getDBConnectionByType, getDBConnection
from headphones import progress,logger

mig_lock = threading.Lock()

tablelist = ["artists","albums","tracks","allalbums","alltracks","snatched","have","lastfmcloud","descriptions","blacklist","newartists","releases"] 

def migrateFrom():
    with mig_lock:
        sqlite = getDBConnectionByType("sqliteAdapter")
        mysql = getDBConnectionByType("mysqlAdapter")
        
        dbp = progress.get("Database Migration",desc="Copy tables from sqllite to target DB",mod=__name__,max=len(tablelist))
        for idx,tbl in enumerate(tablelist):
            mysql.tableCopyFrom(sqlite,tbl)
            dbp.update(idx, tbl)

def migrateTo():
    with mig_lock:
        sqlite = getDBConnectionByType("sqliteAdapter")
        mysql = getDBConnectionByType("mysqlAdapter")
        
        dbp = progress.get("Database Migration",desc="Copy tables from source DB to sqlite",mod=__name__,max=len(tablelist))
        for idx,tbl in enumerate(tablelist):
            tableCopy(mysql,sqlite,tbl)
            dbp.update(idx, tbl)
            
def export():
    with mig_lock:
        db = getDBConnection()
        dbp = progress.get("Database Export",desc="Copy tables from current DB to sqlite",mod=__name__,max=len(tablelist))
        for idx,tbl in enumerate(tablelist):
            db.tableExport(tbl)
            dbp.update(idx, tbl)
            
def tableCopy(sc,tc,tableName):
    # get me a cursor
    cnt = sc.selectOne("SELECT COUNT(*) as total FROM "+tableName)['total'] 
    c=sc.connection.cursor()
    dbt = progress.get("Table Copy",desc="Copy Table " + tableName,mod=__name__,max=cnt)
    rowcnt = 0
    for row in c.execute("SELECT * from "+tableName):
        # assemble insert statement
        i = "INSERT INTO " + tableName + "( " + ",".join(row.keys()) + " )"
        i = i + " VALUES ( " + ", ".join("?" * len(row.keys())) + " )"
        args = row
        try:
            tc.insert(i,args)
        except Exception as e:
            logger.warn("Statement %s : %s" % (i,e))
        dbt.update(rowcnt,"Insert")
        rowcnt = rowcnt + 1
    return