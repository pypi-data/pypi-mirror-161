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
"""Package to make color conversions and operations"""
import math


#*************************************************
#
#*************************************************
def DecToHex(red, green, blue):
    """Convert RGB color to HEX value for HTML"""
    red = int(red * 255)
    green = int(green * 255)
    blue = int(blue * 255)
    return f'#{red:02x}{green:02x}{blue:02x}'


#*************************************************
#
#*************************************************
def ScaleBtoRtoY(val, minVal, maxVal):
    """Return Generate Scaled Color from Blue to Red to Yellow """

    # Normalize to 0-1
    try:
        ratio = float(val-minVal)/(maxVal-minVal)
    except ZeroDivisionError:
        ratio = 0.5

    blue  = min((max((4*(0.75-ratio), 0.)), 1.))
    red   = min((max((4*(ratio-0.25), 0.)), 1.))
    green = min((max((4*math.fabs(ratio-0.5)-1., 0.)), 1.))
    return DecToHex(red, green, blue)

#*************************************************
#
#*************************************************
def ScaleRedtoGreen(val, minVal, maxVal, k = 1):
    """Return Generate Scaled Color from Red to Green """

    # Normalize to 0-1
    try:
        ratio = float(val-minVal)/(maxVal-minVal)
    except ZeroDivisionError:
        ratio = 0.5

    red   = min(max(1-ratio,0.0) * 2,1.0)
    green = min(max(ratio,0.0) * 2,1.0)
    blue = min(red, green) * k
    return DecToHex(red, green, blue)

#*************************************************
#
#*************************************************
def Scale3Step(val, minVal, midVal, maxVal):
    """Return Generate Scaled Color from White to Green(mid value) to Red.  Used for Wind Speed"""

    extVal = ((maxVal - minVal) * 2) + minVal

    if val < minVal:
        red = green = blue = 1.
    elif val <= midVal:
        ratio = float(val-minVal)/(midVal-minVal)
        green = 1.
        blue = red = 1. - ratio
    elif val <= maxVal:
        ratio = float(val-midVal)/(maxVal-midVal)
        red = min(ratio * 2., 1.)
        green = min((1. - ratio) * 2, 1.)
        blue = 0.

    elif val <= extVal:
        ratio = float(val-maxVal)/(extVal-maxVal)
        red = 1.
        green = 0.
        blue = ratio

    else: red = green = blue = 0.

    return DecToHex(red, green, blue)


#*************************************************
#
#*************************************************
def ColorScaleTests():
    """Generate an HTML page to test and display the Color Scaling"""


    html = '<table style="border-collapse: collapse; border: 1px solid #999">'
    styleTh = 'style="border: 1px solid #999; width: 40px; text-align: center; font-size: 10px"'
    styleTd = 'style="border: 1px solid #999; width: 40px; text-align: center; font-size: 10px"'


    html += f'''
    <tr>
    <th {styleTh}>Value</th>
    <th {styleTh}>ScaleBtoRtoY</th>
    <th {styleTh}>ScaleRedtoGreen</th>
    <th {styleTh}>Scale3Step</th>
    </tr>'
    '''
    for i in range(0,100):
        row = '<tr>'
        row += f'<td {styleTd}>{i}</td>'
        colorHex = ScaleBtoRtoY(i,0,100)
        row += f'<td style="border: 1px solid #999; width: 40px; text-align: center; font-size: 10px; background-color: {colorHex}">{colorHex}</td>'
        row += f'<td style="border: 1px solid #999; width: 40px; text-align: center; font-size: 10px; background-color: {colorHex}">{colorHex}</td>'
        colorHex = Scale3Step(i,5, 15, 25)
        row += f'<td style="border: 1px solid #999; width: 40px; text-align: center; font-size: 10px; background-color: {colorHex}">{colorHex}</td>'

        row += '</tr>'
        html += row

    html += '</table>'
    return html

#*************************************************
#
#*************************************************
if __name__ == "__main__":


    #print(f'ColorDecToHex(1,1,1) -> {ColorDecToHex(0.5,0,0.25)}')

    theHTML = ColorScaleTests()
    #--------------------------------
    # Save to File
    #--------------------------------
    FILENAME = 'colors.cache.html'
    try:
        with open(FILENAME, 'w', newline='', encoding='utf-8') as htmlfile:
            htmlfile.write(theHTML)

    except IOError:
        print(f"Count not write to: {FILENAME}")
