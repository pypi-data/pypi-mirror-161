"""Module Produce the Wind Reports to show in HTML and send by email"""
#!/usr/bin/python
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


#--------------------------------
#
#--------------------------------
import os
import pprint
import logging
import datetime
import pytz

import boto3

import o7lib.weather.ca_wls as wls
import o7lib.weather.ca_mf as mf
import o7lib.weather.openweather as owm
import o7lib.weather.planetos as po
import o7lib.util.conversion
import o7lib.util.color


# create logger
logger = logging.getLogger('wind_report')
logger.setLevel(logging.DEBUG)

weekDaysStr=["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
tzEastern = pytz.timezone('US/Eastern')

#*************************************************
#
#*************************************************
def SendEmail(toEmail, subject, message):
    """Send an email with AWS SES"""

    email_client = boto3.client('ses', region_name='ca-central-1')
    fromEmail = "windreport@o7conseils.com"

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.send_email
    resp = email_client.send_email(
        Source=fromEmail,
        Destination={'ToAddresses': [toEmail]},
        Message={
            'Subject': {'Data': subject, 'Charset': 'UTF-8'},
            'Body': {'Html': { 'Data': message,'Charset': 'UTF-8'} }
        }
    )
    print(f'Sent Email to {toEmail} with subject {subject}')



#*************************************************
#
#*************************************************
def MergeHourlyForecast(windOwm = None, windNam = None, waterLevels = None, waterHilos = None, days=2):
    """Merge hourly forecash from different sources"""

    now = datetime.datetime.utcnow()
    dtStart = now.replace( minute = 0, second = 0, microsecond = 0)

    ret = []

    for dtu in (dtStart + datetime.timedelta(hours=1*it) for it in range(24 * days)):

        eastTime = tzEastern.normalize(dtu.astimezone(tz=pytz.utc))

        entry = {
            'dtu' : dtu.isoformat(),
            'dtl' : eastTime.isoformat(),
            'wl' : {}
        }

        theDtu = entry['dtu'][0:13]

        #----------------------
        # Merge Data from Water Level
        #----------------------
        if waterLevels is not None:
            for wl in waterLevels:
                if wl["dtu"][0:13] == theDtu :
                    entry['wl']['value'] = wl['value']
                    break

        if waterHilos is not None:
            for whl in waterHilos:
                if whl["dtu"][0:13] == theDtu :
                    #print(f'whl -> {whl}')
                    entry['wl']['hilo'] = whl['dtl'][11:16]
                    break

        #----------------------
        # Merge Data from Open Weather Map
        #----------------------
        if windOwm is not None:
            for wo in windOwm:
                if wo["dtu"][0:13] == theDtu :
                    #print(f'wo -> {wo}')
                    entry['owm'] = {
                        'wind' : wo['wind'],
                        'gust' : wo['gust'],
                        'deg' :  wo['deg']
                    }
                    break

        #----------------------
        # Merge Data from NAM
        #----------------------
        if windNam is not None:
            for wn in windNam:
                if wn["dtu"][0:13] == theDtu :
                    #print(f'wo -> {wo}')
                    entry['nam'] = {
                        'wind' : wn['wind'],
                        'deg' :  wn['deg']
                    }
                    break


        #print(f'entry -> {entry}')
        ret.append(entry)

    return ret




#*************************************************
#
#*************************************************
def ForecastHtml(forecasts) -> str:
    """Convert forecast to HTML"""

    pprint.pprint(forecasts)

    html = ''

    for f in forecasts:
        html += f''' <b>{f["title"]}</b><br>
        {f["summary"]}<br><br>
        '''

    return html

#*************************************************
#
#*************************************************
def TideHiloTableHtml(tides):
    """Convert High/Low Tide table to HTML"""

    #pprint.pprint(tides)

    html = '<table style="border-collapse: collapse; border: 1px solid #999">'
    theDay = None
    theRow = 0
    styleTd = 'style="border: 1px solid #999; width: 80px; text-align: center; font-size: 10px"'
    styleTrHigh = 'style="background-color: #aaffaa;"'
    styleTrLow = 'style="background-color: #ffaaaa;"'
    styleTrTop = 'style="background-color: #f0f0f0;"'


    # rows = [
    #     f"<th {styleTd}>Date</th>",
    #     f"<th {styleTd}>Basse</th>",
    #     f"<th {styleTd}>Haute</th>",
    #     f"<th {styleTd}>Basse</th>",
    #     f"<th {styleTd}>Haute</th>",
    #     f"<th {styleTd}>Basse</th>",
    # ]
    rows = [ "","","","","",""]

    for tide in tides:

        day = tide["dtl"][:10]
        time = tide["dtl"][11:16]
        value = tide["value"]


        if theDay is None or day != theDay:

            if theDay is not None:
                for i in range(theRow, len(rows)) : rows[i] += f'<td  {styleTd}></td>'

            theDay = day
            weekDay = datetime.datetime.fromisoformat(tide["dtl"]).weekday()
            rows[0] += f'<th {styleTd}>{day}<br>{weekDaysStr[weekDay]}</th>'
            theRow = 1
            if value > 2 :
                rows[theRow] += f'<td {styleTd}></td>'
                theRow += 1

        rows[theRow] += f'<td {styleTd}>{time} ({value} m)</td>'
        theRow += 1

    # Complete last column
    for i in range(theRow, len(rows)) : rows[i] += f'<td {styleTd}></td>'

    for i in range(0, len(rows)):
        if i == 0: html += f'<tr {styleTrTop}>{rows[i]}</tr>'
        elif i % 2 == 1 : html += f'<tr {styleTrLow}>{rows[i]}</tr>'
        elif i % 2 == 0 : html += f'<tr {styleTrHigh}>{rows[i]}</tr>'

    html += '</table>'
    return html

#*************************************************
#
#*************************************************
def ForecastHourlyHtml(hourlys):
    """Convert the Hourly forecast to HMTL"""

    # pprint.pprint(hourlys)

    firstHour = 6
    lasthour = 21
    newDay = True

    styleBasic = 'border: 1px solid #999; width: 40px; text-align: center; font-size: 10px;'

    html = '<table style="border-collapse: collapse; border: 1px solid #999">'
    styleTh = f'style="{styleBasic}"'

    # Header Row
    html += f'''
    <tr>
        <th rowspan=2 {styleTh}>Hour</th>
        <th colspan=3 {styleTh}>Open Weather</th>
        <th colspan=2 {styleTh}>Nam</th>
        <th colspan=1 {styleTh}>WLS</th>
    </tr>
    <tr>
        <th colspan=1 {styleTh}>Wind</th>
        <th colspan=1 {styleTh}>Gust</th>
        <th colspan=1 {styleTh}>Dir</th>
        <th colspan=1 {styleTh}>Wind</th>
        <th colspan=1 {styleTh}>Dir</th>
        <th colspan=1 {styleTh}>Tide</th>
    </tr>
    '''

    r = 0
    for h in hourlys:

        r += 1

        #print(f'hour -> {h}')
        dt = datetime.datetime.fromisoformat(h["dtl"])

        # Check if viewable hour
        if dt.hour < firstHour or dt.hour > lasthour:
            newDay = True
            continue

        # Add Row with Day Information
        if newDay:

            html += f'''
            <tr>
            <th colspan=7 style="{styleBasic} background-color:#999999; color:#ffffff"> {weekDaysStr[dt.weekday()]} ({h["dtl"][0:10]})</th>
            </tr>
            '''
            newDay = False


        print(f'{r}.{h}')
        # Skip irrelevnt lines
        if 'owm' not in h and 'hilo' not in h['wl'] : continue

        row = '<tr>'
        row += f'<td style="{styleBasic} background-color:#ffffff;">{h["dtl"][11:13]}</td>'

        if 'owm' in h:
            val = round(h['owm']['wind'])
            hexColor = o7lib.util.color.Scale3Step(val, 5, 10, 25)
        else : val = ''; hexColor = '#ffffff'
        row += f'<td style="{styleBasic} background-color:{hexColor};">{val}</td>'

        if 'owm' in h:
            val = round(h['owm']['gust'])
            hexColor = o7lib.util.color.Scale3Step(val, 5, 10, 25)
        else : val = ''; hexColor = '#ffffff'
        row += f'<td style="{styleBasic} background-color:{hexColor};">{val}</td>'

        if 'owm' in h:
            val = o7lib.util.conversion.DirectionDegToTxt(h['owm']['deg'])
            hexColor = hexColor = '#ffffff'
        else : val = ''; hexColor = '#ffffff'
        row += f'<td style="{styleBasic} background-color:{hexColor};">{val}</td>'

        if 'nam' in h:
            val = round(h['nam']['wind'])
            hexColor = o7lib.util.color.Scale3Step(val, 5, 10, 25)
        else : val = ''; hexColor = '#ffffff'
        row += f'<td style="{styleBasic} background-color:{hexColor};">{val}</td>'

        if 'nam' in h:
            val = o7lib.util.conversion.DirectionDegToTxt(h['nam']['deg'])
            hexColor = hexColor = '#ffffff'
        else : val = ''; hexColor = '#ffffff'
        row += f'<td style="{styleBasic} background-color:{hexColor};">{val}</td>'


        val = ''; hexColor = '#ffffff'
        if 'wl' in h:
            if 'value' in h['wl'] : hexColor = o7lib.util.color.ScaleRedtoGreen(h['wl']['value'], 0, 5)
            if 'hilo'  in h['wl'] : val = h['wl']['hilo']
        row += f'<td style="{styleBasic} background-color:{hexColor};">{val}</td>'

        row += '</tr>'
        html += row

    html += '</table>'
    return html


#*************************************************
#
#*************************************************
def WindReportHtml(lon, lat, siteId = 23100):
    """Generate Wind Report for a Specific Site"""

    logger = logging.getLogger('wind_report.WindReportHtml')
    logger.debug(f'Parameters ->lon: {lon}  lat: {lat}')

    days = 5

    #----------------------
    # Get data from the Water Level Service
    #----------------------
    theStation = wls.GetClosestStation(lon, lat)
    if theStation is None: return None

    logger.debug(f'WindReportHtml found station: {theStation["officialName"]}')
    waterHilos = wls.GetTidesHiLo(theStation["id"], days=days)
    waterLevels = wls.GetTidesSerie(theStation["id"], days=days)
    lastTemp = wls.GetLastTemperature(theStation["id"])


    #----------------------
    # Get data from National Weather Forecasting
    #----------------------
    forecastText = mf.GetForecast(siteId)

    #----------------------
    # Get wind forecast
    #----------------------
    owmHourlys = owm.OpenWmApi().GetHourlyForecast(lon=lon, lat=lat)
    namAG5 = po.PlanetOsApi().GetNamWindAboveGround3(lon=lon, lat=lat)

    #----------------------
    # Merge all hourly sources
    #----------------------
    hourlys = MergeHourlyForecast(waterLevels=waterLevels, waterHilos=waterHilos, windOwm=owmHourlys, windNam=namAG5, days=days)

    styleTitle = "style='font-size: 14px; font-weight: bold;'"
    styleSection = "style='background-color: #f0f0f0; padding: 5px 5px 5px 10px;'"


    #pprint.pprint(theStation)

    html = '<!DOCTYPE html><html>'
    html += f'''<body>
    <div lang=EN-US style='font-family: "Montserrat", Sans-serif; font-size: 12px; color: #485061; background-color: #ffffff; width=600px;'>
    Bon Matin Capitaine,<br>
    <br>
    Rapport Quotidien pour: <b>{theStation["officialName"]}</b><br>
    <br>

    <span {styleTitle}>Meteo Maritime (<a href='https://meteo.gc.ca/marine/forecast_f.html?mapID=12&siteID=23100'>Env. Canada</a>)</span><br>
    <div {styleSection}>
    {ForecastHtml(forecastText)}
    </div>
    <br>

    <span {styleTitle}>Prévision 48 Heures <a href='https://openweathermap.org/weathermap?basemap=map&cities=true&layer=temperature&lat={lat}&lon={lon}&zoom=10'>(plus d'info)</a>  </span>
    <div {styleSection}>
    {ForecastHourlyHtml(hourlys=hourlys)}
    </div>
    <br>


    <span {styleTitle}>Table des Marées {days} jours <a href='https://tides.gc.ca/fra/station?sid=3248'>(plus d'info)</a>  </span>
    <div {styleSection}>
    {TideHiloTableHtml(waterHilos)}
    Température de l'eau: <b>{lastTemp[0]} C</b> ({lastTemp[1][0:10]})
    </div>
    <br>



    Bonne Journée !
    </div></body></html>
    '''

    return html

#*************************************************
#
#*************************************************
def SendWindReport(email):
    """Send a Wind Report to a email for the Baie de Beau port location"""

    html = WindReportHtml(-71.1948, 46.8424)

    today = datetime.date.today().isoformat()
    title = f'Wind Report for {today}'

    SendEmail(
        toEmail=email,
        subject=title,
        message=html
    )


#*************************************************
#
#*************************************************
def lambda_handler(event, context):
    """Lambda handler to send the wind report"""
    print('event -> ' , event)
    print('context -> ' , context)

    email=os.getenv('EMAIL', None)

    if email is None:
        print('EMAIL ENV VARIABLE IS MISSING')
        return 1

    SendWindReport(email)

    return 0


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    id = '5cebf1e23d0f4a073c4bc0f6'
    lon = -71.1948
    lat = 46.8424


    #theHTML = WindReportHtml(lon, lat)

    # forecastHourly = owm.GetHourlyForecast(-71.1948, 46.8424)

    # waterLevels = wls.GetTidesSerie(id, 5)
    # waterHilos = wls.GetTidesHiLo(id, 5)
    owmHourlys = owm.OpenWmApi().GetHourlyForecast(lon=lon, lat=lat)
    pprint.pprint(owmHourlys)


    # hourlys = MergeHourlyForecast(waterLevels=waterLevels, waterHilos=waterHilos, windOwm=owmHourlys, days=5)
    # #pprint.pprint(hourlys)
    # theHTML = ForecastHourlyHtml(hourlys)


    #--------------------------------
    # Save to File
    #--------------------------------
    # filname = 'wind_report.cache.html'
    # try:
    #     with open(filname, 'w', newline='') as htmlfile:
    #         htmlfile.write(theHTML)

    # except IOError:
    #     print(f"Count not write to: {filname}")

