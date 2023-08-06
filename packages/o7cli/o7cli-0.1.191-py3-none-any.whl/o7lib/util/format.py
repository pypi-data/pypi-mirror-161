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

# python -m unittest tests.test_util_format

"""Package to format some values of object to string """

import datetime
import o7lib.util.conversion


#*************************************************
#
#*************************************************
def Datetime(value, dateFormat = '%Y-%m-%d %H:%M:%S'):
    """Convert a DateTime (object or unix int) into a Text Form"""

    #print(f'FormatDatetime Value Type {type(value)}')
    if value is None:
        return ''

    dtClass = o7lib.util.conversion.ToDatetime(value)
    if isinstance(dtClass, datetime.datetime) is False:
        return ''

    return dtClass.strftime(dateFormat)


#*************************************************
#
#*************************************************
def ElapseTime(value):
    """Convert a DateTime or Seconds (int) into Text about the elapse time (ex: 6 sec, 3.2 min)"""

    # print(f'FormatSince Value Type {type(value)} {value=}')
    timeUnits = [
        {'txt': 'sec', 'scale' : 60.0},
        {'txt': 'min', 'scale' : 60.0},
        {'txt': 'hr', 'scale' : 24.0},
        {'txt': 'day', 'scale' : 365.0},
        {'txt': 'yr', 'scale' : 100.0},
        {'txt': 'ct', 'scale' : 100.0}
    ]

    if value is None:
        return ''

    since = o7lib.util.conversion.ToElapseSenconds(value)
    unit = 'NA'

    if since is None:
        return unit

    # Convert and fine unit
    for timeUnit in timeUnits:
        unit = timeUnit['txt']
        if since < timeUnit['scale']:
            break
        since = since / timeUnit['scale']

    return f'{since:.1f} {unit}'

#*************************************************
#
#*************************************************
def Bytes(value):
    """Convert a Byte Value into Text (ex: 16 B, 345 MB)"""

    # print(f'FormatSince Value Type {type(value)} {value=}')
    byteUnits = [
        {'txt': 'B', 'scale' : 1024},
        {'txt': 'KB', 'scale' : 1024},
        {'txt': 'MB', 'scale' : 1024},
        {'txt': 'GB', 'scale' : 1024},
        {'txt': 'TB', 'scale' : 1024},
        {'txt': 'PB', 'scale' : 1024}
    ]

    if value is None:
        return ''

    bytesValue = float(value)
    unit = 'NA'

    # Convert and fine unit
    for byteUnit in byteUnits:
        unit = byteUnit['txt']
        if bytesValue < byteUnit['scale']:
            break
        bytesValue = bytesValue / byteUnit['scale']

    return f'{bytesValue:.1f} {unit}'
