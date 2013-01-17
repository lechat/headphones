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

__all__ = [ "dbMigration", "Mysql", "Sqlite"]

import headphones
from os import sys

def getDBModule(name):
#    name=name.lower()
    prefix = 'headphones.databases.'
    fullname = prefix + name + 'Adapter'
    if fullname in sys.modules:
        return sys.modules[fullname]
    else:
        raise Exception("Can't find %s in %s" % (fullname, repr(sys.modules)))
    
def getDBConnection(db_type=headphones.DB_MODE):
    module = getDBModule(db_type)
    class_name = db_type + 'DBConnection'
    return module.class_name()

def getDBList():
    databases = []
    for db_module in __all__:
        mod =  getDBConnection(db_module)
        name = mod.dbNiceName()
        databases.append([db_module, name])
    return databases