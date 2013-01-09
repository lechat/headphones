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

from __future__ import with_statement

import sqlite3, time, os
import headphones, csv, unicodecsv

from headphones import logger,db,progress

class DBConnection:

    def __init__(self, filename="headphones.db"):
    
        if headphones.MYSQL_DB == None or headphones.MYSQL_DB == "":
            headphones.MYSQL_DB = "headphones"
        self.filename = headphones.MYSQL_DB+".db"
        self.connection = sqlite3.connect(db.dbFilename(filename), timeout=20)
        #don't wait for the disk to finish writing
        self.connection.execute("PRAGMA synchronous = OFF")
        #journal disabled since we never do rollbacks
        self.connection.execute("PRAGMA journal_mode = OFF")        
        #64mb of cache memory,probably need to make it user configurable
        self.connection.execute("PRAGMA cache_size=-%s" % (db.getCacheSize()*1024))
        self.connection.row_factory = sqlite3.Row
        
    def selectOne(self,sql,args=None):
        sqlResults = self.action(sql, args).fetchone()
        if sqlResults == None:
            return []
            
        return sqlResults

    def insert(self,sql,args=None):
        self.action(sql, args)
        
    
    def update(self,sql,args=None):
        self.action(sql, args)
    
    def delete(self,sql,args=None):
        self.action(sql, args)
        
    def action(self, query, args=None):
    
        with db.db_lock:

            if query == None:
                return
                
            sqlResult = None
            attempt = 0
            
            while attempt < 5:
                try:
                    if args == None:
                        #logger.debug(self.filename+": "+query)
                        sqlResult = self.connection.execute(query)
                    else:
                        #logger.debug(self.filename+": "+query+" with args "+str(args))
                        sqlResult = self.connection.execute(query, args)
                    self.connection.commit()
                    break
                except sqlite3.OperationalError, e:
                    if "unable to open database file" in e.message or "database is locked" in e.message:
                        logger.warn('Database Error: %s' % e)
                        attempt += 1
                        time.sleep(1)
                    else:
                        logger.error('Database error: %s' % e)
                        raise
                except sqlite3.DatabaseError, e:
                    logger.error('Fatal Error executing %s :: %s' % (query, e))
                    raise
            
            return sqlResult
            
    def tableExport(self,tableName):
        cnt = self.selectOne("SELECT COUNT(*) as total FROM "+tableName)['total'] 
        c=self.connection.cursor()
        rows = c.execute("SELECT * from "+tableName)
        dbt = progress.get("Table Export",desc="Export tables to filesystem as CSV " + tableName,mod=__name__,max=cnt)
        rowcnt = 0
        with open(os.path.join(headphones.DATA_DIR, tableName+'.csv'),'wb') as csvfile:
            try:
                writer = unicodecsv.writer(csvfile,quoting=csv.QUOTE_ALL,escapechar="\\")
                writer.writerow([t[0] for t in c.description])
                for row in rows:
                    try:
                        writer.writerow(list(row))
                        dbt.update(rowcnt,"Insert")
                        rowcnt = rowcnt + 1
                    except Exception as e:
                        logger.warn("Export line(%i) error: %s" % (rowcnt,e))
            except Exception as e:
                logger.warn("Export error: %s" % e)
        return        
    
    def selectSome(self,query,off,lim, args=None ):
        r = []
        try:
            query = query + " LIMIT " + str(lim) + " OFFSET " + str(off)
            r = self.select(query,args)
        except Exception as e:
            logger.info("Failed limited select: %s" % e )
        return r
    
    def select(self, query, args=None):
    
        sqlResults = self.action(query, args).fetchall()
        
        if sqlResults == None:
            return []
            
        return sqlResults
                    
    def upsert(self, tableName, valueDict, keyDict):
    
        changesBefore = self.connection.total_changes
        
        genParams = lambda myDict : [x + " = ?" for x in myDict.keys()]
        
        query = "UPDATE "+tableName+" SET " + ", ".join(genParams(valueDict)) + " WHERE " + " AND ".join(genParams(keyDict))
        s1 = time.time()
        self.action(query, valueDict.values() + keyDict.values())
        s2 = time.time()
        if self.connection.total_changes == changesBefore:
            
            query = "INSERT INTO "+tableName+" (" + ", ".join(valueDict.keys() + keyDict.keys()) + ")" + \
                        " VALUES (" + ", ".join(["?"] * len(valueDict.keys() + keyDict.keys())) + ")"
            self.action(query, valueDict.values() + keyDict.values())
        if (time.time() - s1) > 0.5:
            logger.warn("Timings for upsert: %f(update), %f(insert)" % ( s2 - s1, time.time() - s2 ))

def dbNiceName():
    return "SQL Lite"

def maintenance():
    conn=sqlite3.connect(headphones.DB_FILE)
    c=conn.cursor()
    logger.info("checking for DB problems...")
    try:
        r = c.execute("PRAGMA integrity_check").fetchall()
        for p in r:
            logger.error("DB check reports problem: %s" % p[0])
    except:
        logger.error("DB integrity check failed.")
    logger.info("Cleaning and defragmenting DB")
    try:
        c.execute("VACUUM")
    except:
        logger.error("Cleanup failed.")
    logger.info("Gathering Statistics")
    try:
        c.execute("ANALYZE")
    except:
        logger.error("ANALYZE failed.")
    conn.commit()
    c.close()
    return

def dbcheck():

    conn=sqlite3.connect(headphones.DB_FILE)
    c=conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS artists (ArtistID VARCHAR(255) UNIQUE, ArtistName VARCHAR(255), ArtistSortName TEXT, DateAdded TEXT, Status TEXT, IncludeExtras INTEGER, LatestAlbum TEXT, ReleaseDate TEXT, AlbumID VARCHAR(255), HaveTracks INTEGER, TotalTracks INTEGER, LastUpdated TEXT, ArtworkURL TEXT, ThumbURL TEXT, startDate TEXT, endDate TEXT, Extras TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS albums (ArtistID VARCHAR(255), ArtistName VARCHAR(255), AlbumTitle TEXT, AlbumASIN TEXT, ReleaseDate VARCHAR(255), DateAdded TEXT, AlbumID VARCHAR(255) UNIQUE, Status TEXT, Type TEXT, ArtworkURL TEXT, ThumbURL TEXT, ReleaseID VARCHAR(100), ReleaseCountry TEXT, ReleaseFormat TEXT)')   # ReleaseFormat here means CD,Digital,Vinyl, etc. If using the default Headphones hybrid release, ReleaseID will equal AlbumID (AlbumID is releasegroup id)
    c.execute('CREATE TABLE IF NOT EXISTS tracks (ArtistID VARCHAR(255), ArtistName VARCHAR(255), AlbumTitle TEXT, AlbumASIN TEXT, AlbumID VARCHAR(255), TrackTitle TEXT, TrackDuration TIME, TrackID VARCHAR(255), TrackNumber INTEGER, Location TEXT, BitRate INTEGER, CleanName TEXT, Format TEXT, ReleaseID VARCHAR(100))')    # Format here means mp3, flac, etc.
    c.execute('CREATE TABLE IF NOT EXISTS allalbums (ArtistID VARCHAR(255), ArtistName VARCHAR(255), AlbumTitle TEXT, AlbumASIN TEXT, ReleaseDate TEXT, AlbumID VARCHAR(255), Type TEXT, ReleaseID VARCHAR(100), ReleaseCountry TEXT, ReleaseFormat TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS alltracks (ArtistID VARCHAR(255), ArtistName VARCHAR(255), AlbumTitle TEXT, AlbumASIN TEXT, AlbumID VARCHAR(255), TrackTitle TEXT, TrackDuration TIME, TrackID VARCHAR(255), TrackNumber INTEGER, Location TEXT, BitRate INTEGER, CleanName TEXT, Format TEXT, ReleaseID VARCHAR(100))')
    c.execute('CREATE TABLE IF NOT EXISTS snatched (AlbumID VARCHAR(255), Title TEXT, Size INTEGER, URL TEXT, DateAdded TEXT, Status TEXT, FolderName TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS have (ArtistName VARCHAR(255), AlbumTitle TEXT, TrackNumber TEXT, TrackTitle TEXT, TrackLength TEXT, BitRate TEXT, Genre TEXT, Date TEXT, TrackID VARCHAR(255), Location TEXT, CleanName TEXT, Format TEXT, Matched TEXT)') # Matched is a temporary value used to see if there was a match found in alltracks
    c.execute('CREATE TABLE IF NOT EXISTS lastfmcloud (ArtistName VARCHAR(255), ArtistID VARCHAR(255), Count INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS descriptions (ArtistID VARCHAR(255), ReleaseGroupID VARCHAR(100), ReleaseID VARCHAR(100), Summary TEXT, Content TEXT, LastUpdated TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS blacklist (ArtistID VARCHAR(255) UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS newartists (ArtistName VARCHAR(255) UNIQUE)')
    c.execute('CREATE TABLE IF NOT EXISTS releases (ReleaseID VARCHAR(100), ReleaseGroupID VARCHAR(100), UNIQUE(ReleaseID, ReleaseGroupID))')

    c.execute('CREATE INDEX IF NOT EXISTS tracks_albumid ON tracks(AlbumID ASC)')
    c.execute('CREATE INDEX IF NOT EXISTS album_artistid_reldate ON albums(ArtistID ASC, ReleaseDate DESC)')
    c.execute("CREATE INDEX IF NOT EXISTS tracks_artistid ON Tracks(ArtistID ASC)")
    c.execute("CREATE INDEX IF NOT EXISTS alltracks_trackid_releaseid ON alltracks(TrackID,ReleaseID)")
    c.execute("CREATE INDEX IF NOT EXISTS alltracks_trackid_albumtitle ON alltracks(TrackID,AlbumTitle)")
    c.execute("CREATE INDEX IF NOT EXISTS tracks_trackid_albumid ON tracks(TrackID,AlbumId)")
    c.execute("CREATE INDEX IF NOT EXISTS tracks_trackid_releaseid ON tracks(TrackID,ReleaseID)")
    c.execute("CREATE INDEX IF NOT EXISTS tracks_trackid_albumtitle ON tracks(TrackID,AlbumTitle)")
    c.execute("CREATE INDEX IF NOT EXISTS tracks_trackid_albumid ON tracks(TrackID,AlbumId)")
    
    try:
        c.execute('SELECT IncludeExtras from artists')
    except:
        c.execute('ALTER TABLE artists ADD COLUMN IncludeExtras INTEGER DEFAULT 0')
        
    try:
        c.execute('SELECT LatestAlbum from artists')
    except:
        c.execute('ALTER TABLE artists ADD COLUMN LatestAlbum TEXT')
        
    try:
        c.execute('SELECT ReleaseDate from artists')
    except:
        c.execute('ALTER TABLE artists ADD COLUMN ReleaseDate TEXT')
        
    try:
        c.execute('SELECT AlbumID from artists')
    except:
        c.execute('ALTER TABLE artists ADD COLUMN AlbumID VARCHAR(255)')
        
    try:
        c.execute('SELECT HaveTracks from artists')
    except:
        c.execute('ALTER TABLE artists ADD COLUMN HaveTracks INTEGER DEFAULT 0')
        
    try:
        c.execute('SELECT TotalTracks from artists')
    except:
        c.execute('ALTER TABLE artists ADD COLUMN TotalTracks INTEGER DEFAULT 0')
        
    try:
        c.execute('SELECT Type from albums')
    except:
        c.execute('ALTER TABLE albums ADD COLUMN Type TEXT DEFAULT "Album"')

    try:
        c.execute('SELECT TrackNumber from tracks')
    except:
        c.execute('ALTER TABLE tracks ADD COLUMN TrackNumber INTEGER')
        
    try:
        c.execute('SELECT FolderName from snatched')
    except:
        c.execute('ALTER TABLE snatched ADD COLUMN FolderName TEXT')
    
    try:
        c.execute('SELECT Location from tracks')
    except:
        c.execute('ALTER TABLE tracks ADD COLUMN Location TEXT')
        
    try:
        c.execute('SELECT Location from have')
    except:
        c.execute('ALTER TABLE have ADD COLUMN Location TEXT')
    
    try:
        c.execute('SELECT BitRate from tracks')
    except:
        c.execute('ALTER TABLE tracks ADD COLUMN BitRate INTEGER')  
        
    try:
        c.execute('SELECT CleanName from tracks')
    except:
        c.execute('ALTER TABLE tracks ADD COLUMN CleanName TEXT')  
        
    try:
        c.execute('SELECT CleanName from have')
    except:
        c.execute('ALTER TABLE have ADD COLUMN CleanName TEXT')  
    
    # Add the Format column
    try:
        c.execute('SELECT Format from have')
    except:
        c.execute('ALTER TABLE have ADD COLUMN Format TEXT DEFAULT NULL')  
    
    try:
        c.execute('SELECT Format from tracks')
    except:
        c.execute('ALTER TABLE tracks ADD COLUMN Format TEXT DEFAULT NULL')
        
    try:
        c.execute('SELECT LastUpdated from artists')
    except:
        c.execute('ALTER TABLE artists ADD COLUMN LastUpdated TEXT DEFAULT NULL')
        
    try:
        c.execute('SELECT ArtworkURL from artists')
    except:
        c.execute('ALTER TABLE artists ADD COLUMN ArtworkURL TEXT DEFAULT NULL') 
        
    try:
        c.execute('SELECT ArtworkURL from albums')
    except:
        c.execute('ALTER TABLE albums ADD COLUMN ArtworkURL TEXT DEFAULT NULL') 
        
    try:
        c.execute('SELECT ThumbURL from artists')
    except:
        c.execute('ALTER TABLE artists ADD COLUMN ThumbURL TEXT DEFAULT NULL') 
        
    try:
        c.execute('SELECT ThumbURL from albums')
    except:
        c.execute('ALTER TABLE albums ADD COLUMN ThumbURL TEXT DEFAULT NULL') 
        
    try:
        c.execute('SELECT ArtistID from descriptions')
    except:
        c.execute('ALTER TABLE descriptions ADD COLUMN ArtistID TEXT DEFAULT NULL') 
        
    try:
        c.execute('SELECT LastUpdated from descriptions')
    except:
        c.execute('ALTER TABLE descriptions ADD COLUMN LastUpdated TEXT DEFAULT NULL') 
        
    try:
        c.execute('SELECT ReleaseID from albums')
    except:
        c.execute('ALTER TABLE albums ADD COLUMN ReleaseID TEXT DEFAULT NULL')
        
    try:
        c.execute('SELECT ReleaseFormat from albums')
    except:
        c.execute('ALTER TABLE albums ADD COLUMN ReleaseFormat TEXT DEFAULT NULL')
        
    try:
        c.execute('SELECT ReleaseCountry from albums')
    except:
        c.execute('ALTER TABLE albums ADD COLUMN ReleaseCountry TEXT DEFAULT NULL')
        
    try:
        c.execute('SELECT ReleaseID from tracks')
    except:
        c.execute('ALTER TABLE tracks ADD COLUMN ReleaseID TEXT DEFAULT NULL')
        
    try:
        c.execute('SELECT Matched from have')
    except:
        c.execute('ALTER TABLE have ADD COLUMN Matched TEXT DEFAULT NULL')
        
    try:
        c.execute('SELECT startDate from artists')
    except:
        c.execute('ALTER TABLE artists ADD COLUMN startDate TEXT DEFAULT NULL')
        
    try:
        c.execute('SELECT endDate from artists')
    except:
        c.execute('ALTER TABLE artists ADD COLUMN endDate TEXT DEFAULT NULL')
        
    try:
        c.execute('SELECT Extras from artists')
    except:
        c.execute('ALTER TABLE artists ADD COLUMN Extras TEXT DEFAULT NULL')
        # Need to update some stuff when people are upgrading and have 'include extras' set globally/for an artist
        if headphones.INCLUDE_EXTRAS:
            headphones.EXTRAS = "1,2,3,4,5,6,7,8"
        logger.info("Copying over current artist IncludeExtras information")
        artists = c.execute('SELECT ArtistID, IncludeExtras from artists').fetchall()
        for artist in artists:
            if artist[1]:
                c.execute('UPDATE artists SET Extras=? WHERE ArtistID=?', ("1,2,3,4,5,6,7,8", artist[0]))
    
    conn.commit()    
    c.close()
