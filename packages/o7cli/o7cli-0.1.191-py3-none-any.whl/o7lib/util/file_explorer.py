#!/usr/bin/env python
#************************************************************************
# Copyright 2021 O7 Conseils inc (Philippe Gosselin)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#************************************************************************

"""Package to explores files & directories """

import os
import pathlib
#import pprint
import o7lib.util.input
import o7lib.util.displays



#*************************************************
#
#*************************************************
class FileExplorer():
    """Class to explore files & directories"""

    #*************************************************
    #
    #*************************************************
    def __init__(self, cwd = '.'):

        self.cwd = os.path.realpath(cwd)


    #*************************************************
    #
    #*************************************************
    def ScanDirectory(self, filters = None):
        """List all files in the current directory """
        files = []

        # https://docs.python.org/3/library/os.html#os.scandir
        with os.scandir(path = self.cwd) as entries:
            for entry in entries:

                # https://docs.python.org/3/library/os.html#os.stat_result
                stats = entry.stat()
                #print(f'{entry.name} - stats: {stats}')

                fType = ''
                size = stats.st_size
                extention = None
                if entry.is_dir():
                    fType += 'd'
                    size = None
                if entry.is_file():
                    fType += 'f'
                    extention = pathlib.Path(entry.path).suffix

                if entry.is_symlink():
                    fType += 's'

                if filters is not None:
                    if entry.is_file():
                        if 'extensions' in filters:
                            if extention not in filters['extensions']:
                                continue

                files.append({
                    'name': entry.name,
                    'path' : entry.path,
                    'type' : fType,
                    'size' : size,
                    'extention': extention,
                    #'created': stats.st_birthtime,
                    'updated' : stats.st_mtime
                })

        # Sort list
        files.sort(key=lambda x: x.get('type') + x.get('name'))


        return files

    #*************************************************
    #
    #*************************************************
    def DiplayDirectory(self, filters = None):
        """Display the Current Directory"""

        #diskUsage = shutil.disk_usage(self.cwd)
        cwdList = self.ScanDirectory(filters = filters)
        # print('Disk Usage')
        # pprint.pprint(diskUsage)

        # print('list Dir')
        # pprint.pprint(cwdList)
        params = {
            'title' : f'Active Directory: {self.cwd}',
            'columns' : [
                {'title' : 'id'      , 'type': 'i',       'minWidth' : 4  },
                {'title' : 'Type'    , 'type': 'str',  'dataName': 'type'},
                {'title' : 'Name'    , 'type': 'str',  'dataName': 'name'},
                {'title' : 'Size'    , 'type': 'bytes',  'dataName': 'size'},
                {'title' : 'Extension'    , 'type': 'str',  'dataName': 'extention'},
                {'title' : 'Updated', 'type': 'since', 'dataName': 'updated'}
            ]
        }
        o7lib.util.displays.Table(params, cwdList)

        return cwdList




    #*************************************************
    #
    #*************************************************
    def SelectFile(self, filters = None):

        while True :
            cwdList = self.DiplayDirectory(filters = filters)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Parent(p) Remove Filters (r) Select File (int): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    return None

                if key.lower() == 'p':
                    self.cwd = pathlib.Path(self.cwd).parent

                if key.lower() == 'r':
                    filters= None

            if keyType == 'int' and key > 0 and key <= len(cwdList):
                print(f'Selected File : {cwdList[key - 1]["path"]}')
                file = cwdList[key - 1]
                if file["type"] == 'd':
                   self.cwd = file['path']
                else:
                    return file['path']


#*************************************************
# To Test Class
#*************************************************
if __name__ == "__main__":


    theFE = FileExplorer(cwd = '.')
    theFE.SelectFile()
