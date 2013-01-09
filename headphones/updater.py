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

from headphones import logger, databases, importer, progress

def dbUpdate():
    
    myDB = databases.getDBConnection()

    activeartists = myDB.select('SELECT ArtistID, ArtistName from artists WHERE Status="Active" or Status="Loading" order by LastUpdated ASC')

    logger.info('Starting update for %i active artists' % len(activeartists))
    
    p = progress.get("Database Update",desc="Update artists",mod=__name__,max=len(activeartists))
    p.message = "in progress"
    
    for idx,artist in enumerate(activeartists):
        artistid = artist['ArtistID']
        importer.addArtisttoDB(artistid, False,True)
        p.update(idx,artist['ArtistName'])
    
    p.message = "complete"
    logger.info('Update complete')
