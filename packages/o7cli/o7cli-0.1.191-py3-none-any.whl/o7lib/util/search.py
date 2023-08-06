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

"""Package with useful search function Functions """


import json


#*************************************************
#
#*************************************************
def ValueInDict(dataKey, data):
    """Search a Dict data structure for a specified name.  key.key format can be used"""

    if data is None or isinstance(data, dict) is False:
        return None

    value = data.get(dataKey, None)
    if value is not None:
        return value

    # Try to find value by spliting keys with .
    for i, key in enumerate(dataKey.split(".")):
        #print(f'-> {i} - {key}')
        if i == 0:
            value = data.get(key, None)
        else:
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.decoder.JSONDecodeError:
                    return None

            value = value.get(key, None)

        #print(f'{value=}')

        if value is None:
            return None

    return value
