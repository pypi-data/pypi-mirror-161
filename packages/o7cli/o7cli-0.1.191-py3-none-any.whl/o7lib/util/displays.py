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

"""Package for Console Display Util Functions """

import datetime
import shutil
import os

import sty

import o7lib.util.search
import o7lib.util.conversion
import o7lib.util.format
import o7lib.util.terminal as o7t

os.system("") # Fix issue with Terminal colors in windows


#*************************************************
# https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
# https://github.com/feluxe/sty
#*************************************************
class Colors:
    """Constant for Console Colors  """
    HEADER = sty.fg.black + sty.bg.li_grey
    RED = sty.fg.li_red
    GREEN = sty.fg.li_green
    YELLOW = sty.fg.li_yellow
    BLUE = sty.fg.blue
    MAGENTA =  sty.fg.magenta
    CYAN = sty.fg.cyan
    WHITE = sty.fg.white
    ORANGE = sty.fg(255, 150, 50)

    INPUT =  sty.fg.li_magenta
    ACTION = sty.fg(255, 150, 50)

    OK = sty.fg.li_green
    WARNING = sty.fg.li_yellow
    ERROR = sty.fg.li_red
    FAIL = sty.fg.li_red
    ALARM = sty.fg.li_red

    BOLD = sty.ef.bold
    ITALIC = sty.ef.italic
    UNDERLINE = sty.ef.italic

    ENDC = sty.rs.all
    ENDF = sty.rs.fg

#*************************************************
#
#*************************************************
def GetTerminalWidth():
    """Get the width of current terminal window"""
    columns = shutil.get_terminal_size()[0]
    return columns


#*************************************************
#
#*************************************************
def ConsoleLine(left = "", center = "", right = ""):
    """Display a  titles using the full console wisth"""

    line = center.center(GetTerminalWidth(), ' ')
    line = left + line[len(left):]
    line = line[:(len(right)*(-1))] + right


    print(f"{line}")

#*************************************************
#
#*************************************************
def ConsoleTitleLine(left = "", center = "", right = ""):
    """Display a  titles using the full console width"""

    title = center.center(GetTerminalWidth(), ' ')
    title = left + title[len(left):]
    title = title[:(len(right)*(-1))] + right


    print(f"{Colors.HEADER}{title}{Colors.ENDC}")

#*************************************************
#
#*************************************************
def ClearDisplay():
    """Clear Console"""
    print("\033[H\033[J", end="")

#*************************************************
#
#*************************************************
def ConsoleTitle(left = "", center = "", right = ""):
    """Clear Console & add Title"""
    ClearDisplay()
    ConsoleTitleLine(left, center, right)

#*************************************************
#
#*************************************************
def PrintParamError(name, value):
    """Print a parameters in Error colors"""
    print(f'{name}: {Colors.ERROR}{value}{Colors.ENDF}')

#*************************************************
#
#*************************************************
def PrintError(txt):
    """Print a line in Error colors"""
    print(f'{Colors.ERROR}{txt}{Colors.ENDF}')

#*************************************************
#
#*************************************************
def PrintParamWarning(name, value):
    """Print a parameters in Error colors"""
    print(f'{name}: {Colors.WARNING}{value}{Colors.ENDF}')

#*************************************************
#
#*************************************************
def PrintWarning(txt):
    """Print a line in Warning colors"""
    print(f'{Colors.WARNING}{txt}{Colors.ENDF}')

#*************************************************
#
#*************************************************
def PrintParamOk(name, value, isOk = True):
    """Print a parameters in Error colors"""
    if isOk:
        print(f'{name}: {Colors.OK}{value}{Colors.ENDF}')
    else:
        PrintParamError(name, value)


#*************************************************
#
#*************************************************
def FormatAlarm(val):
    """Return the value with alarm format"""
    return f"{Colors.ALARM}{val}{Colors.ENDF}"


#*************************************************
#
#*************************************************
def FormatNormal(val):
    """Return the value with normal format"""
    return f"{Colors.OK}{val}{Colors.ENDF}"



#*************************************************
#
#*************************************************
def Table(params, datas):
    """
    Print a Table on Screen from parameters and a data array.

    Args:
        params (dict):
            title (string): Table Tile
            columns (list): Each elements defines a column
                [{
                    type: Data type, options
                        i = index in array (1 ... lenght)
                        str = string
                        date = datetime displayed in format YYYY-MM-DD
                        datetime =  datetime displayed in format YYYY-MM-DD HH:MM:SS
                        since =  Duration between value and now (must be a datetime)
                    dataName : Key name in the data list
                    title : Column name to display

                    maxWidth : Maximum Width for a column
                    minWidth : Minimum Width for a column
                    fixWidth : Column is for a to a specific width

                    format : Special formating for this column, options
                        aws-status
                        aws-state  (EC2 States)
                        aws-drift
                }...]

        datas (list): Each element is a Row (or Data)


    """

    columns = params.get('columns', [])
    tableWidth = 0
    consoleWidth = GetTerminalWidth()
    formatedDatas = list({} for i in range(len(datas)))

    #----------------------------
    # Loop to prepare data
    #----------------------------
    for col in columns :

        dataType = col.get('type', 'str')
        if dataType == 'i':
            col['dataName'] = 'i'

        dataName = col.get('dataName', 'not-set')

        maxW = col.get('maxWidth', None)
        minW = col.get('minWidth', None)
        fixW = col.get('fixWidth', None)

        alarmVal = col.get('alarm', None)
        normalVal = col.get('normal', None)

        width = len(col.get('title', ''))

        for i, data in enumerate(datas):

            # Get and Transform data
            index = i + 1

            # Get value with support of "." enumeration
            value = o7lib.util.search.ValueInDict(dataName, data)

            formatedData = {
                'raw': value,
                'isAlm' : False,
                'isNormal' : False,
                'value' : None
            }

            # Verify if in alarm
            if alarmVal is not None:
                if alarmVal == value:
                    formatedData['isAlm'] = True
            if normalVal is not None:
                if normalVal == value:
                    formatedData['isNormal'] = True

            # Reformat Value
            if dataType == 'i':
                value = str(index)
            elif value is None:
                value = ''
            elif dataType == 'date':
                value = o7lib.util.format.Datetime(value, '%Y-%m-%d')
            elif dataType == 'datetime' and value is not None:
                value = o7lib.util.format.Datetime(value, '%Y-%m-%d %H:%M:%S')
            elif dataType == 'since':
                value = o7lib.util.format.ElapseTime(value)
            elif dataType == 'bytes':
                value = o7lib.util.format.Bytes(value)

            else: value = str(value)

            value = value.replace('\n', ' ')
            formatedData['value'] = value

            formatedDatas[i][dataName] = formatedData
            width = max(width, len(value))

        if maxW is not None:
            width = min(width, maxW)
        if minW is not None:
            width = max(width, minW)
        if fixW is not None:
            width = fixW

        # make sure we dont overflow terminal
        widthLeft =  consoleWidth - (tableWidth + 3)
        if widthLeft <= 3:
            width = 0
        else:
            width = min(width,widthLeft)
            tableWidth += width + 3

        col['width'] = width

    #----------------------------
    # Loop to build top tow
    #----------------------------
    topRow = ''
    for col in columns :
        colWidth = col.get('width')
        if colWidth < 1:
            continue
        title = col.get('title', '')[0:colWidth]
        title = title.center(colWidth, ' ')
        topRow += f" {title} |"

    #----------------------------
    # Print Title and Top Row
    #----------------------------
    title = params.get('title', None)
    if title is not None:
        title = title.center(tableWidth, ' ')
        print(f"{Colors.HEADER}{title}{Colors.ENDC}")

    print(f"{Colors.HEADER}{topRow}{Colors.ENDC}")


    #----------------------------
    # Loop to print all data Rows
    #----------------------------
    for data in formatedDatas:
        dataRow = ''
        for col in columns :
            dataName = col.get('dataName', 'not set')
            colWidth = col.get('width')
            colFormat = col.get('format', '')

            if colWidth < 1:
                continue

            formatedData = data.get(dataName, {})
            val = formatedData['value']
            val = val[0:colWidth].ljust(colWidth, ' ')
            isAlarm = formatedData['isAlm']
            isNormal = formatedData['isNormal']


            if isAlarm is True:
                val = FormatAlarm(val)
            elif isNormal is True:
                val = FormatNormal(val)
            elif colFormat == 'aws-status':
                val = o7t.FormatAWSStatus(val)
            elif colFormat == 'aws-drift':
                val = o7t.FormatAWSDrift(val)
            elif colFormat == 'aws-state':
                val = o7t.FormatAWSState(val)

            dataRow += f" {val} |"

        print(dataRow)

    bottomRow = " " * tableWidth
    print(f"{Colors.HEADER}{bottomRow}{Colors.ENDC}")



#*************************************************
# To Test Class
#*************************************************
if __name__ == "__main__":

    theParams = {
            'title' : "Cloudformation Stacks for region: TBD",
            'columns' : [
                {'title' : 'id'      , 'type': 'i',       'width' : 4  },
                {'title' : 'Name'    , 'type': 'str',     'width' : 40, 'dataName': 'StackName'},
                {'title' : 'Creation', 'type': 'date',    'width' : 2, 'dataName': 'CreationTime', 'format': '%Y-%m-%d'},
                {'title' : 'Status'  , 'type': 'str',     'width' : 2, 'dataName': 'StackStatus'}
            ]
    }
    theDatas = [
        {'StackName' : 'first-stack', 'CreationTime': datetime.datetime(2021, 8, 23), 'StackStatus': 'COMPLETE'},
        {'StackName' : 'second-stack', 'CreationTime': datetime.datetime(2021, 8, 23), 'StackStatus': 'UPDATING'},
    ]

    Table(theParams, theDatas)
