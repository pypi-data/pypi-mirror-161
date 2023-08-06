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

"""Package to display array in a table format (console, HTML...) """

import datetime

import o7lib.util.search
import o7lib.util.format
import o7lib.util.conversion
import o7lib.util.terminal as o7t

# Ref
# Charaters for boxes: https://en.wikipedia.org/wiki/Box-drawing_character#Box_Drawing


#*************************************************
#
#*************************************************
class Table():
    """Class to display array in a table format (console, HTML...)"""

    #*************************************************
    #
    #*************************************************
    def __init__(self, param = None, datas = None):
        """
        Args:
            params (dict):
                title (string): Table Tile
                columns (list): Each elements defines a column
                    [{
                        title : Column name to display
                        type: Data type, options
                            i = index in array (1 ... lenght)
                            str = string
                            int = integer
                            float = float point numbers
                            date = datetime displayed in format YYYY-MM-DD
                            datetime =  datetime displayed in format YYYY-MM-DD HH:MM:SS
                            since =  Duration between value and Now (datetime or unix Timestamps or seconds or duration)
                            bytes = format in B or KB or MB.... depemding on size
                        dataName : Key name in the data list

                        maxWidth : Maximum Width for a column
                        minWidth : Minimum Width for a column
                        fixWidth : Column is for a to a specific width

                        alarm : Value equal to for alarm format
                        normal : Value equal to for normal format
                        alarmHi : Alarm when Value is equal or above
                        alarmLo : Alarm when Value is equal or below
                        warningHi : Warning when Value is above or below
                        warningLo : Warning when Value is equal or below

                        sort: (asc or des) If the data should be sort on this columns


                        format : Special formating for this column, options
                            aws-status
                            aws-state  (EC2 States)
                            aws-drift
                            aws-edit
                    }...]
        """

        self.rawDatas = []
        self.processDatas = None
        self.title = ''
        self.terminalTableWidth = 0
        self.columns = []
        self.sorted = {}

        if param is not None:
            self.Configure(param)

        if datas is not None:
            self.UpdateData(datas)


    #*************************************************
    #
    #*************************************************
    def Configure(self, param):
        """Configure the table with provided parameters"""

        self.processDatas = None
        self.title = param.get('title', '')
        self.columns = []
        self.sorted = {}
        columns = param.get('columns', [])

        #----------------------------
        # Loop to prepare data
        #----------------------------
        for column in columns :

            dataType = column.get('type', 'str')

            dataName = 'not-set'
            if dataType == 'i':
                dataName = 'i'
            dataName = column.get('dataName', dataName)

            title = column.get('title', '')

            newColumn = {
                'title' : title,
                'type' : dataType,
                'dataName' : dataName,

                'width' : len(title),
                'widthTerm' : 0,
                'maxW' : column.get('maxWidth', None),
                'minW' : column.get('minWidth', None),
                'fixW' : column.get('fixWidth', None),
                'dataW' : 0,

                'alarmVal' : column.get('alarm', None),
                'alarmHi' : column.get('alarmHi', None),
                'alarmLo' : column.get('alarmLo', None),
                'warningHi' : column.get('warningHi', None),
                'warningLo' : column.get('warningLo', None),
                'normalVal' : column.get('normal', None),

                'format': column.get('format', None)

            }

            sort =  column.get('sort', None)
            if sort is not None:
                self.sorted[dataName] = sort


            self.columns.append(newColumn)



    #*************************************************
    #
    #*************************************************
    def UpdateData(self, datas):
        """Update the Raw Data"""

        self.rawDatas = datas
        self.processDatas = None

        for column, order in self.sorted.items():
            self.rawDatas = sorted(self.rawDatas, key=lambda x: x[column])

    #*************************************************
    #
    #*************************************************
    def ProcessData(self):
        """Analyse raw data and prepare dtata for output"""

        # prepare array to receive the process data
        self.processDatas = list({} for i in range(len(self.rawDatas)))

        self.terminalTableWidth = 0
        consoleWidth = o7t.GetWidth()

        for column in self.columns :
            dataWidth = 0
            for i, data in enumerate(self.rawDatas):

                # Get and Transform data
                index = i + 1

                # Get value with support of "." enumeration
                rawValue = o7lib.util.search.ValueInDict(column['dataName'], data)
                dataType = column['type']

                processData = {
                    'raw': rawValue,
                    'eng': rawValue,
                    'isAlm' : False,
                    'isWarn' : False,
                    'isNormal' : False,
                    'value' : None
                }

                #---------------------
                # Convert Eng Value, when required
                #---------------------
                if dataType == 'since':
                    processData['eng'] = o7lib.util.conversion.ToElapseSenconds(rawValue)
                if dataType == 'int':
                    processData['eng'] = o7lib.util.conversion.ToInt(rawValue)
                if dataType == 'float':
                    processData['eng'] = o7lib.util.conversion.ToFloat(rawValue)

                engValue = processData['eng']

                #---------------------
                # Verify if in a special state (alarm, warning, normal)
                #---------------------
                if engValue is not None:
                    if column['alarmVal'] is not None:
                        if column['alarmVal'] == engValue:
                            processData['isAlm'] = True

                    if column['alarmHi'] is not None:
                        if engValue >= column['alarmHi']:
                            processData['isAlm'] = True

                    if column['alarmLo'] is not None:
                        if engValue <= column['alarmLo']:
                            processData['isAlm'] = True

                    if column['warningHi'] is not None:
                        if engValue >= column['warningHi']:
                            processData['isWarn'] = True

                    if column['warningLo'] is not None:
                        if engValue <= column['warningLo']:
                            processData['isWarn'] = True

                    if column['normalVal'] is not None:
                        if column['normalVal'] == engValue:
                            processData['isNormal'] = True


                #---------------------
                # Reformat Value
                #---------------------
                if dataType == 'i':
                    newValue = str(index)
                elif rawValue is None:
                    newValue = ''
                elif dataType == 'date':
                    newValue = o7lib.util.format.Datetime(engValue, '%Y-%m-%d')
                elif dataType == 'datetime':
                    newValue = o7lib.util.format.Datetime(engValue, '%Y-%m-%d %H:%M:%S')
                elif dataType == 'since':
                    newValue = o7lib.util.format.ElapseTime(engValue)
                elif dataType == 'bytes':
                    newValue = o7lib.util.format.Bytes(engValue)
                else:
                    newValue = str(engValue)

                newValue = newValue.replace('\n', ' ')
                processData['value'] = newValue

                self.processDatas[i][column['dataName']] = processData
                dataWidth = max(dataWidth, len(newValue))

            #----------------
            # Calculate the appropriate column width
            #----------------
            column['dataW'] = dataWidth
            column['width'] = max(column['width'], dataWidth)

            if column['maxW'] is not None:
                column['width'] = min(column['width'], column['maxW'])
            if column['minW'] is not None:
                column['width'] = max(column['width'], column['minW'])
            if column['fixW'] is not None:
                column['width'] = column['fixW']

            #----------------
            # Calculate the column width in a temrinal windows
            #----------------
            # make sure we dont overflow terminal
            widthLeft =  consoleWidth - (self.terminalTableWidth + 3)
            if widthLeft <= 3:
                column['widthTerm'] = 0
            else:
                column['widthTerm'] = min(column['width'],widthLeft)
                self.terminalTableWidth += column['widthTerm'] + 3



    #*************************************************
    #
    #*************************************************
    def PrintHeader(self):

        """Print Table Header to console"""
        #----------------------------
        # Loop to build top tow
        #----------------------------
        topRow = ''
        for column in self.columns :
            width = column['widthTerm']
            if width < 1:
                continue
            title = column['title'][0:width]
            title = title.center(width, ' ')
            topRow += f" {title} \U00002502"

        #----------------------------
        # Print Title and Top Row
        #----------------------------
        if self.title is not None and len(self.title) > 0:
            title = self.title.center(self.terminalTableWidth, ' ')
            o7t.PrintHeader(title)

        o7t.PrintHeader(topRow)


    #*************************************************
    #
    #*************************************************
    def PrintRows(self):
        """Print all data row in temrminal"""

        for row in self.processDatas:

            dataRow = ''
            for column in self.columns :

                width = column['widthTerm']
                if  width < 1:
                    continue

                dataName = column['dataName']
                processData = row[dataName]

                value = processData['value']
                value = value[0:width].ljust(width, ' ')

                colFormat = column['format']
                isAlarm = processData['isAlm']
                isWarning = processData['isWarn']
                isNormal = processData['isNormal']


                if isAlarm is True:
                    value = o7t.FormatAlarm(value)
                elif isWarning is True:
                    value = o7t.FormatWarning(value)
                elif isNormal is True:
                    value = o7t.FormatNormal(value)
                elif colFormat == 'aws-status':
                    value = o7t.FormatAWSStatus(value)
                elif colFormat == 'aws-drift':
                    value = o7t.FormatAWSDrift(value)
                elif colFormat == 'aws-edit':
                    value = o7t.FormatAWSEdit(value)
                elif colFormat == 'aws-state':
                    value = o7t.FormatAWSState(value)

                dataRow += f" {value} \U00002502"

            print(dataRow)

    #*************************************************
    #
    #*************************************************
    def PrintFooter(self):
        """Print Footer in temrminal"""
        bottomRow = " " * self.terminalTableWidth
        o7t.PrintHeader(bottomRow)

    #*************************************************
    #
    #*************************************************
    def Print(self, datas = None):
        """Print Table to console"""

        if datas is not None:
            self.UpdateData(datas)

        if self.processDatas is None:
            self.ProcessData()

        self.PrintHeader()
        self.PrintRows()
        self.PrintFooter()


#*************************************************
# To Test Class
#*************************************************
if __name__ == "__main__":

    import pprint


    theParams = {
            'title' : "Cloudformation Stacks for region: ca-central-1",
            'columns' : [
                {'title' : 'id'      , 'type': 'i',       },
                {'title' : 'Name'    , 'type': 'str',     'minWidth' : 40, 'dataName': 'StackName'},
                {'title' : 'Creation', 'type': 'date',    'maxWidth' : 10, 'dataName': 'CreationTime', 'format': '%Y-%m-%d'},
                {'title' : 'Updated'  , 'type': 'since',     'dataName': 'UpdateTime'},
                {'title' : 'Status'  , 'type': 'str',     'fixWidth' : 15, 'dataName': 'StackStatus', 'format' : 'aws-status'},
                {'title' : 'Alert'  , 'type': 'str',     'dataName': 'Alert', 'alarm' : True, 'normal' : False}
            ]
    }
    theDatas = [
        {'StackName' : 'first-stack', 'CreationTime': datetime.datetime(2021, 8, 23),
        'UpdateTime': datetime.datetime(2021, 8, 24), 'StackStatus': 'COMPLETE', 'Alert' : True
        },
        {'StackName' : 'second-stack','CreationTime': datetime.datetime(2021, 8, 23),
        'UpdateTime': datetime.datetime(2021, 10, 24),'StackStatus': 'UPDATING', 'Alert' : False
        },
    ]

    theTable = Table(param = theParams)
    theTable.UpdateData(datas = theDatas)
    pprint.pprint(theTable.columns, indent=4,sort_dicts=False)
    pprint.pprint(theTable.processDatas, indent=4,sort_dicts=False)

    theTable.Print()
