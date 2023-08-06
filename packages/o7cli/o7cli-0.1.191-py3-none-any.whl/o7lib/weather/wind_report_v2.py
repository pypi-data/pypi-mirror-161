"""Module Produce the Wind Reports to show in HTML"""
#!/usr/bin/python
#************************************************************************
# Copyright 2022 O7 Conseils inc (Philippe Gosselin)
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


#--------------------------------
#
#--------------------------------
import math
import logging
import typing

import pandas as pd

import o7lib.weather.location
import o7lib.util.conversion
import o7lib.util.color


# create logger
logger = logging.getLogger(__name__)


weekDaysStr=["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


#*************************************************
#
#*************************************************
class WindReport(): # pylint: disable=too-many-instance-attributes
    """Class Generate Wind Report for list of location"""

    def __init__(
        self,
        locations: typing.List[o7lib.weather.location.Location] = [],
        forecasts: typing.List[dict] = []
        ) -> None:

        self.locations : typing.List[o7lib.weather.location.Location] = locations
        self.forecasts : typing.List[dict] = forecasts

        self.firstHour = 6
        self.lastHour = 20

        self.ssTd = 'border: 1px solid #999; width: 40px; text-align: center; font-size: 10px;'
        self.ssSpace = 'width:1px; background-color:#000000;'


    #*************************************************
    #
    #*************************************************
    def GenerateTideTd(self, data : pd.Series, minVal: float, maxVal: float) -> str:
        """Generate HTML for a tide cell"""

        txt = ''
        color = '#ffffff'
        if math.isnan(data['hilo']) is False:
            txt = f'{int(data["hour"]):02}:{int(data["hilo"]):02}'

        if math.isnan(data['height']) is False:
            color = o7lib.util.color.ScaleRedtoGreen(val = data['height'], minVal=minVal, maxVal=maxVal)


        return f'<td style="{self.ssTd} background-color:{color};">{txt}</td>'


    #*************************************************
    #
    #*************************************************
    def GenerateWindTd(self, data : pd.Series, colName : str = 'wind') -> str:
        """Generate HTML for a wind cell"""

        txt = ''
        color = '#ffffff'
        if math.isnan(data[colName]) is False:
            txt = str(int(data[colName]))
            color = o7lib.util.color.Scale3Step(data[colName], 7, 12, 25)

        return f'<td style="{self.ssTd} background-color:{color};">{txt}</td>'


    #*************************************************
    #
    #*************************************************
    def GenerateGustTd(self, data : pd.Series, colName : str = 'wind') -> str:
        """Generate HTML for a gust cell"""
        return self.GenerateWindTd(data, colName='gust')


    #*************************************************
    #
    #*************************************************
    def GenerateDirectionTd(self, data : pd.Series, colName : str = 'deg') -> str:
        """Generate HTML for a direction cell"""

        txt = ''
        color = '#ffffff'
        if math.isnan(data[colName]) is False:
            txt = o7lib.util.conversion.DirectionDegToTxt(data[colName])

        return f'<td style="{self.ssTd} background-color:{color};">{txt}</td>'

    #*************************************************
    #
    #*************************************************
    def GenerateNewDayTr(self, data : pd.Series) -> str:
        """Generate HTML the beginning of a new day"""

        txt = ''
        if data['new'] is True:
            width = 1 + (5 * len(self.locations))
            cell = f'{weekDaysStr[data["day"]]} {str(data.name)[0:10]}'
            txt = f'<tr><td colspan={width} style="{self.ssTd} background-color:#999999; color:#ffffff">{cell}</td></tr>'
        return txt

    #*************************************************
    #
    #*************************************************
    def GenerateHourlyHeaderTrs(self) -> str:
        """Create Table Header"""

        styleTh = f'style="{self.ssTd}"'
        htmlLocationTh1 : str = ''
        htmlLocationTh2 : str = ''
        html :str = ""

        for location in self.locations:
            htmlLocationTh1 += f'<th style="{self.ssSpace}"></th><th colspan=4 {styleTh}><a href="{location.gmapUrl}">{location.name}</a></th>'
            htmlLocationTh2 += f'<th style="{self.ssSpace}"></th><th {styleTh}>Vent</th><th {styleTh}>Gust</th>'
            htmlLocationTh2 += f'<th {styleTh}>Dir</th><th {styleTh}><a href="{location.stationWlp.url}">Marée</a></th>'

        html += f'<tr> <th rowspan=2 {styleTh}>H</th> {htmlLocationTh1}</tr>'
        html += f'<tr>{htmlLocationTh2}</tr>'

        return html



    #*************************************************
    #
    #*************************************************
    def GenerateHourlyWindTidesTrs(self) -> str:
        """Convert & Filter Hourly data for all location in corrected timezone"""

        dfHtml : pd.DataFrame = None
        html = ""

        for i, location in enumerate(self.locations):

            # Convert to local time
            dfLocal = location.hourlyForecast.tz_convert('US/Eastern', copy=True)

            # Get max and min tide for each location
            tideMax = dfLocal['height'].max()
            tideMin = dfLocal['height'].min()

            # Remove rows out of time range
            dfLocal = dfLocal[dfLocal.index.hour >= self.firstHour]
            dfLocal = dfLocal[dfLocal.index.hour <= self.lastHour]

            dfLocal['hour'] = dfLocal.index.hour

            # On the first location, create table & first columns
            if dfHtml is None:
                dfHtml = pd.DataFrame(index=dfLocal.index)

                dfLocal['day'] = dfLocal.index.weekday
                dfLocal['new'] = dfLocal['day'] != dfLocal['day'].shift(1)
                dfHtml['new'] = dfLocal.apply(self.GenerateNewDayTr, axis = 1)

                dfHtml['st']  = '<tr>'
                dfHtml['h']   = dfLocal['hour'].apply(lambda x: f'<td style="{self.ssTd}">{x:02}</td>')


            # Round Wind values
            dfLocal['wind'] = dfLocal['wind'].round()
            dfLocal['gust'] = dfLocal['gust'].round()

            # pd.set_option('display.min_rows', 20)
            # pd.set_option('display.max_colwidth', 20)
            # print(dfLocal[0:5])

            dfHtml[f'{i}_Space'] = f'<td style="{self.ssSpace}"></td>'
            dfHtml[f'{i}_Wind']  = dfLocal.apply(self.GenerateWindTd, axis = 1)
            dfHtml[f'{i}_Gust']  = dfLocal.apply(self.GenerateGustTd, axis = 1)
            dfHtml[f'{i}_Dir']   = dfLocal.apply(self.GenerateDirectionTd, axis = 1)
            dfHtml[f'{i}_Tide']  = dfLocal.apply(self.GenerateTideTd, axis = 1, args=(tideMin, tideMax))

        if dfHtml is not None:
            dfHtml['end'] = '</tr>'

            # pd.set_option('display.min_rows', 20)
            # pd.set_option('display.max_colwidth', 15)
            # print(dfHtml[0:5])
            html = dfHtml.apply(lambda x: x.str.cat(sep=''), axis=1).str.cat(sep='\n')

        return html

    #*************************************************
    #
    #*************************************************
    def GenerateWaterTempTrs(self) -> str:
        """Rows with Location Water Temperature"""

        width = 1 + (5 * len(self.locations))
        html = f'<tr><td colspan={width} style="{self.ssTd} background-color:#999999; color:#ffffff">Temperature de l\'eau</td></tr>'

        row1 = '<tr><td></td>'
        row2 = '<tr><td></td>'

        for location in self.locations:
            row1 += f'<td style="{self.ssSpace}"></td>'
            row2 += f'<td style="{self.ssSpace}"></td>'

            date = str(location.lastWaterTemp.dtu)[0:10]

            row1 += f'<td colspan=4  style="{self.ssTd}"><b>{location.lastWaterTemp.value}&deg;C</b> ({date})</td>'
            row2 += f'<td colspan=4  style="{self.ssTd}"> {location.stationWt.name} ({location.stationWt.distance:.1f}km)</td>'

        row1 += '</tr>'
        row2 += '</tr>'
        html += row1
        html += row2


        return html


    #*************************************************
    #
    #*************************************************
    def ForecastHourlyTable(self) -> str:
        """Convert the Hourly forecast to HMTL"""

        html = '<table style="border-collapse: collapse; border: 1px solid #999">'

        html += self.GenerateHourlyHeaderTrs()
        html += self.GenerateHourlyWindTidesTrs()
        html += self.GenerateWaterTempTrs()


        html += '</table>'
        return html

    #*************************************************
    #
    #*************************************************
    def ExtendedForecast(self) -> str:
        """Convert the Hourly forecast to HMTL"""

        html = ''

        for forecast in self.forecasts:
            html += f'''<a href="{forecast["link"]}"><b>{forecast["title"]}</b></a><br>
            {forecast["summary"]}<br><br>
            '''

        return html



    #*************************************************
    #
    #*************************************************
    def GenerateReportHtml(self) -> str:
        """Generate Wind Report for the locations"""

        styleTitle = "style='font-size: 14px; font-weight: bold;'"
        styleSection = "style='background-color: #f0f0f0; padding: 5px 5px 5px 10px;'"


        html = f'''<!DOCTYPE html><html><body>
        <div lang=EN-US style='font-family: "Montserrat", Sans-serif; font-size: 12px; color: #485061; background-color: #ffffff'>
        Bon Matin Capitaine,<br>
        <br>

        <span {styleTitle}>Prévision 48 Heures</span>
        <div {styleSection}>{self.ForecastHourlyTable()}</div>
        <br>


        <span {styleTitle}>Prévision Maritime Long Terme</span><br>
        <div {styleSection}>{self.ExtendedForecast()}</div>
        <br>

        Bonne Journée !
        </div></body></html>
        '''

        return html


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)


    # baieLon =
    # baieLat = 46.8424
    # berthierLon =
    # berthierLat =

    # neuvilleLon =
    # neuvilleLat =


    baieObj = o7lib.weather.location.Location(lon=-71.1948, lat=46.8424, name='Baie de Beauport')
    baieObj.LoadAllInfo(days=2)
    berthierObj = o7lib.weather.location.Location(lon=-70.7340515, lat=46.9357283, name='Berthier sur Mer')
    berthierObj.LoadAllInfo(days=2)
    neuvilleObj = o7lib.weather.location.Location(lon=-71.5697675, lat=46.6984466, name='Neuville')
    neuvilleObj.LoadAllInfo(days=2)
    stanneObj = o7lib.weather.location.Location(lon=-70.918802, lat=47.0239151, name='Ste-Anne')
    stanneObj.LoadAllInfo(days=2)

    #reportObj = WindReport([baieObj])
    reportObj = WindReport([baieObj, berthierObj])
    reportObj = WindReport([neuvilleObj, baieObj, berthierObj, stanneObj])

    theHTML = reportObj.GenerateReportHtml()

    #--------------------------------
    # Save to File
    #--------------------------------
    filname = 'wind_report.cache.html'
    try:
        with open(filname, 'w', newline='', encoding='utf-8') as htmlfile:
            htmlfile.write(theHTML)

    except IOError:
        print(f"Count not write to: {filname}")




