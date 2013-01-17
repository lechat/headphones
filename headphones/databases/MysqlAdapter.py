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

import headphones

import mysql.connector, csv, os
from mysql.connector import errorcode
from headphones import logger, progress
from headphones.databases.AbstractAdapter import DBConnectionInterface

class DBConnection(DBConnectionInterface):
    def __init__(self):
        super(DBConnection, self).__init__()
        self.connection = None
        self.dbNiceName = 'MYSQL'
        #
        # db connection per thread
        #
        tl = threading.local()
        sqlConnection = getattr(tl, 'sqlConnection', None)
        
        if not sqlConnection:
            try:
                config = {
                          'user': headphones.MYSQL_USER.encode('ascii', 'ignore'),
                          'password': headphones.MYSQL_PASS.encode('ascii', 'ignore'),
                          'host': headphones.MYSQL_SERVER.encode('ascii', 'ignore'),
                          'database': headphones.MYSQL_DB.encode('ascii', 'ignore'),
                          'connection_timeout': 100
                         }
                self.connection = mysql.connector.connect(**config)
                tl.sqlConnection = self.connection
            except mysql.connector.Error as e:
                logger.error('MySQL Database error in init: %s' % e)
            except Exception as ex:
                logger.error('MySQL Error during database connection: %s' % ex)
        else:
            self.connection = tl.sqlConnection
        
    def __del__(self):
        if self.connection:
            self.connection.close()

    def _cursor(self):
        if not self.connection.is_connected():
            self.connection.reconnect(3, 1)
        return self.connection.cursor()

    def _query(self, cursor, sql, args=None):
        #sanitize query string
        sql = sql.strip().replace(' COLLATE NOCASE', '').replace('?','%s')
        if not args:
            cursor.execute(sql)
        else:
            cursor.execute(sql, args)

    #
    # Standard Interface follows.
    #
    def tableExport(self,tableName):
        cnt = self.selectOne('SELECT COUNT(*) as total FROM '+tableName)['total']
        rows = self._cursor()
        rows.execute('SELECT * from %s' % tableName)
        dbt = progress.get('Table Export', desc='Export tables to filesystem as CSV ' + tableName,
                            mod=__name__, max=cnt)
        rowcnt = 0
        with open(os.path.join(headphones.DATA_DIR, tableName + '.csv'), 'wb') as csvfile:
            try:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, escapechar='\\')
                writer.writerow(rows.column_names)
                for row in rows:
                    writer.writerow([v.encode('utf8') for v in row])
                    dbt.update(rowcnt,'Insert')
                    rowcnt += 1
            except Exception as e:
                logger.warn('Export error: %s' % e)
        return

    def tableCopyFrom(self, source, tableName):
        cnt = source.selectOne('SELECT COUNT(*) as total FROM '+tableName)['total']
        c = source.connection.cursor()
        dbt = progress.get('Table Copy', desc='Copy Table ' + tableName, mod=__name__, max=cnt)
        rowcnt = 0
        self.connection.autocommit = False
        c.execute('SELECT * from ' + tableName)
        columns = [t[0] for t in c.description]
        tc = self.connection.cursor()
        row_sql = 'INSERT INTO ' + tableName + '( ' + ','.join(columns) + ' )'
        row_sql = row_sql + ' VALUES ( ' + ', '.join('?' * len(columns)) + ' )'
        row_sql = row_sql.replace('?', '%s')
        while True:
            if self.connection.is_connected() == False:
                self.connection.reconnect(3, 1)
            row = [ list(v) for v in c.fetchmany(20)]
            if row == []:
                break
            try:
                tc.executemany(row_sql, row)
            except mysql.connector.Error as err:
                    logger.warn('Failed to insert(%i): %s' % (err.errno, str(err)))
            except Exception as e:
                logger.warn('Failed to insert: %s' % e)
            dbt.update(rowcnt, 'Insert')
            rowcnt += len(row)

        self.connection.commit()

    def selectOne(self, sql, args=None):
        sqlResults = None
        try:
            sql += ' LIMIT 1'
            c = self._cursor()
            self._query(c, sql ,args)
            sqlResults = c.fetchone()
            if sqlResults:
                sqlResults = dict(zip(c.column_names,sqlResults))
            c.close()
        except mysql.connector.Error as e:
            logger.error('Database error: %s' % e)
        except Exception as ex:
            logger.error('General error: %s' % ex)
            
        return sqlResults

    def selectSome(self, query, off, lim, args=None):
        rows= []
        try:
            query = '{0:>s} LIMIT {1:>s} OFFSET {2:>s}'.format(query, str(lim), str(off))
            rows = self.select(query, args)
        except Exception as e:
            logger.info('Failed limited select: %s' % e )
        return rows
                
    def select(self, sql, args=None):    
        sqlResults = []
        try:
            c = self._cursor()
            self._query(c, sql, args)
            sqlResults = c.fetchall()
            if sqlResults:
                sqlResults = [dict(zip(c.column_names, row)) for row in sqlResults]
            c.close()
        except mysql.connector.Error as e:
            logger.error('Database error: %s' % e)
        except Exception as ex:
            logger.error('General error: %s' % ex)
        
        return sqlResults
    
    def insert(self, sql, args=None):
        try:
            c = self._cursor()
            self._query(c, sql, args)
            c.close()
            self.connection.commit()
        except mysql.connector.Error as e:
            logger.error('Database error: %s' % e)
        except Exception as ex:
            logger.error('General error: %s' % ex)

    def update(self, sql, args=None):
        try:
            c = self._cursor()
            self._query(c, sql, args)
            c.close()
            self.connection.commit()
        except mysql.connector.Error as e:
            logger.error('Database error: %s' % e)
        except Exception as ex:
            logger.error('General error: %s' % ex)

    def delete(self, sql, args=None):
        try:
            c = self._cursor()
            self._query(c, sql, args)
            c.close()
            self.connection.commit()
        except mysql.connector.Error as e:
            logger.error('Database error: %s' % e)
        except Exception as ex:
            logger.error('General error: %s' % ex)
        
    
    def upsert(self, tableName, valueDict, keyDict):
        #
        # NOT Safe!
        #
        sql = None
        genParams = lambda myDict : [x + ' = ?' for x in myDict.keys()]
        try:
            c = self._cursor()
            fdq = 'SELECT COUNT(*) FROM {0:>s} WHERE {1:>s}'.format(tableName, ' AND '.join(genParams(keyDict)))
            self._query(c, fdq, keyDict.values())
            fd = c.fetchone()[0]
            if fd == 0:
                # insert
                sql = 'INSERT INTO %s ( %s )' % (tableName, ','.join(valueDict.keys() + keyDict.keys()))
                sql = '%s VALUES ( %s )' % (sql, ', '.join('?' * len(valueDict.keys() + keyDict.keys())))
                self._query(c, sql, valueDict.values() + keyDict.values())
            else:
                # update 
                sql = 'UPDATE {0:>s} SET {1:>s}'.format(tableName, ','.join(genParams(valueDict)))
                sql = '{0:>s} WHERE {1:>s}'.format(sql, ' AND '.join(genParams(keyDict)))
                self._query(c, sql,valueDict.values() + keyDict.values())
            c.close()
            self.connection.commit()
        except mysql.connector.Error as e:
            logger.error('Database error: %s' % e)
        except Exception as ex:
            logger.error('General error: %s' % ex)
            
    def dbcheck(self):
        try:
            con = mysql.connector.connect(user=headphones.MYSQL_USER.encode('ascii','ignore'),
                                            password=headphones.MYSQL_PASS.encode('ascii','ignore'),
                                            host=headphones.MYSQL_SERVER.encode('ascii','ignore'))
            c = con.cursor()

            # before we do anything else we check for the database
            c.execute('CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET "utf8"'.format(headphones.MYSQL_DB))
            con.database = headphones.MYSQL_DB
            # DDL definitions
            tables = {}
            tables['artists'] = ('CREATE TABLE IF NOT EXISTS artists ( \
                                  ArtistID VARCHAR(100) PRIMARY KEY, \
                                  ArtistName VARCHAR(255), \
                                  ArtistSortName TEXT, \
                                  DateAdded VARCHAR(20), \
                                  Status TEXT, \
                                  IncludeExtras INTEGER, \
                                  LatestAlbum TEXT, \
                                  ReleaseDate VARCHAR(20), \
                                  AlbumID VARCHAR(100), INDEX (AlbumID), \
                                  HaveTracks INTEGER, \
                                  TotalTracks INTEGER, \
                                  LastUpdated VARCHAR(20), \
                                  ArtworkURL TEXT, \
                                  ThumbURL TEXT, \
                                  startDate VARCHAR(20), \
                                  endDate VARCHAR(20), \
                                  Extras TEXT \
                                  )' )
            tables['albums'] = (' CREATE TABLE IF NOT EXISTS albums ( \
                                  ArtistID VARCHAR(100), INDEX (ArtistID), \
                                  ArtistName VARCHAR(255), \
                                  AlbumTitle TEXT, \
                                  AlbumASIN TEXT, \
                                  ReleaseDate VARCHAR(20), \
                                  DateAdded VARCHAR(20), \
                                  AlbumID VARCHAR(255) PRIMARY KEY, \
                                  Status VARCHAR(20), \
                                  Type VARCHAR(255), \
                                  ArtworkURL TEXT, \
                                  ThumbURL TEXT, \
                                  ReleaseID VARCHAR(100), \
                                  ReleaseCountry VARCHAR(255), \
                                  ReleaseFormat TEXT)')
            # ReleaseFormat here means CD,Digital,Vinyl, etc. If using the default Headphones hybrid release,
            # ReleaseID will equal AlbumID (AlbumID is releasegroup id)
            tables['tracks'] = ('CREATE TABLE IF NOT EXISTS tracks (\
                                 ArtistID VARCHAR(100), INDEX (ArtistID), \
                                 ArtistName VARCHAR(255), \
                                 AlbumTitle TEXT, \
                                 AlbumASIN TEXT, \
                                 AlbumID VARCHAR(100), \
                                 TrackTitle TEXT, \
                                 TrackDuration INTEGER, \
                                 TrackID VARCHAR(100), \
                                 TrackNumber INTEGER, \
                                 Location TEXT, \
                                 BitRate INTEGER, \
                                 CleanName TEXT, \
                                 Format TEXT, \
                                 ReleaseID VARCHAR(100), \
                                 PRIMARY KEY (AlbumID,TrackID,ReleaseID) )')
            # Format here means mp3, flac, etc.
            tables['allalbums'] = ('CREATE TABLE IF NOT EXISTS allalbums (\
                                    ArtistID VARCHAR(100), INDEX (ArtistID), \
                                    ArtistName VARCHAR(255), \
                                    AlbumTitle TEXT, \
                                    AlbumASIN TEXT, \
                                    ReleaseDate VARCHAR(20), \
                                    AlbumID VARCHAR(100), \
                                    Type TEXT, \
                                    ReleaseID VARCHAR(100), \
                                    ReleaseCountry TEXT, \
                                    ReleaseFormat TEXT, \
                                    PRIMARY KEY (AlbumID,ReleaseID) ) ')
            tables['alltracks'] = ('CREATE TABLE IF NOT EXISTS alltracks (\
                                    ArtistID VARCHAR(100), INDEX(ArtistID), \
                                    ArtistName VARCHAR(255), \
                                    AlbumTitle TEXT, \
                                    AlbumASIN TEXT, \
                                    AlbumID VARCHAR(100), INDEX (AlbumID), \
                                    TrackTitle TEXT, \
                                    TrackDuration INTEGER, \
                                    TrackID VARCHAR(100), \
                                    TrackNumber INTEGER, \
                                    Location TEXT, \
                                    BitRate INTEGER, \
                                    CleanName TEXT, \
                                    Format TEXT, \
                                    ReleaseID VARCHAR(100), \
                                    PRIMARY KEY ( AlbumID, TrackID , ReleaseID ) )')
            tables['snatched'] = ('CREATE TABLE IF NOT EXISTS snatched (\
                                   AlbumID VARCHAR(100), INDEX (AlbumID), \
                                   Title TEXT, \
                                   Size INTEGER, \
                                   URL TEXT, \
                                   DateAdded VARCHAR(20), \
                                   Status TEXT, \
                                   FolderName TEXT)')
            tables['have'] = ('CREATE TABLE IF NOT EXISTS have (\
                               ArtistName VARCHAR(255), \
                               AlbumTitle TEXT, \
                               TrackNumber TEXT, \
                               TrackTitle TEXT, \
                               TrackLength TIME, \
                               BitRate INTEGER, \
                               Genre TEXT, \
                               Date VARCHAR(20), \
                               TrackID VARCHAR(100), \
                               Location TEXT, \
                               CleanName TEXT, \
                               Format TEXT, \
                               Matched TEXT)')
            # Matched is a temporary value used to see if there was a match found in alltracks
            tables['lastfmcloud'] = ('CREATE TABLE IF NOT EXISTS lastfmcloud (\
                                      ArtistName VARCHAR(255), \
                                      ArtistID VARCHAR(100), INDEX (ArtistID), \
                                      Count INTEGER)')
            tables['descriptions'] = ('CREATE TABLE IF NOT EXISTS descriptions (\
                                       ArtistID VARCHAR(100), INDEX (ArtistID), \
                                       ReleaseGroupID VARCHAR(100), \
                                       ReleaseID VARCHAR(100), \
                                       Summary TEXT, \
                                       Content TEXT, \
                                       LastUpdated VARCHAR(20))')
            tables['blacklist'] = ('CREATE TABLE IF NOT EXISTS blacklist (\
                                    ArtistID VARCHAR(100) PRIMARY KEY)')
            tables['newartists'] = ('CREATE TABLE IF NOT EXISTS newartists (\
                                     ArtistName VARCHAR(255) PRIMARY KEY)')
            tables['releases'] = ('CREATE TABLE IF NOT EXISTS releases (\
                                   ReleaseID VARCHAR(100), \
                                   ReleaseGroupID VARCHAR(100), \
                                   UNIQUE(ReleaseID, ReleaseGroupID))')
            for name,ddl in tables.iteritems():
                try:
                    logger.info('Creating table %s...' % name)
                    c.execute(ddl)
                except mysql.connector.Error as err:
                    if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                        logger.warn('Table %s already exists!' % name)
                    else:
                        logger.error('Error creating table '+name+': %s' % err.errmsg)
                else:
                    logger.info('Created.')

            # DB migration
            try:
                c.execute('SELECT startDate from artists')
            except:
                c.execute('ALTER TABLE artists ADD COLUMN startDate VARCHAR(20) DEFAULT NULL')

            try:
                c.execute('SELECT endDate from artists')
            except:
                c.execute('ALTER TABLE artists ADD COLUMN endDate VARCHAR(20) DEFAULT NULL')

        except Exception as err:
            logger.error(u'Failed to create database {}.'.format(headphones.MYSQL_DB))
        else:
            c.close()
            con.close()