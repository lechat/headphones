# This file is part of Headphones.
#
# Headphones is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

__all__ = [ "dbMigration","mysqlAdapter","sqliteAdapter"]

import headphones
from os import sys

def getDBModule(name):
#    name=name.lower()
    prefix = 'headphones.databases.'
    if prefix+name in sys.modules:
        return sys.modules[prefix+name]
    else:
        raise Exception("Can't find "+prefix+name+" in "+repr(sys.modules))
    
def getDBConnection():
    module = getDBModule(headphones.DB_MODE)
    return module.DBConnection()

def getDBConnectionByType(dbtype):
    module = getDBModule(dbtype)
    return module.DBConnection()

def getDBList():
    l = []
    for m in __all__:
        if m.endswith("Adapter"):
            mod =  getDBModule(m)
            name = mod.dbNiceName()
            l.append([m,name])
    return l