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

#__all__ = [ "dbMigration", "Mysql", "Sqlite"]

import headphones
import os
from os import sys

def import_file(path_to_module):
    """Note: path to module must be a relative path starting from a directory in sys.path"""
    module_dir, module_file = os.path.split(path_to_module)
    module_name, _module_ext = os.path.splitext(module_file)
    module_package = ".".join(module_dir.split(os.path.sep)) + '.' + module_name

    module_obj = __import__(module_package, fromlist=['*'])
    module_obj.__file__ = path_to_module
    return module_obj

def getDBModule(name):
#    name=name.lower()
    prefix = 'headphones/databases/'
    fullname = prefix + name + 'Adapter'
    return import_file(fullname)

def getDBConnection(db_type=None):
    if not db_type:
        db_type = headphones.DB_TYPE
    module = getDBModule(db_type)
    return module.DBConnection()

def getDBList():
    databases = []
    # TODO lechat: deal with this later
#    for db_module in __all__:
#        mod =  getDBConnection(db_module)
#        name = mod.dbNiceName()
#        databases.append([db_module, name])
    return databases