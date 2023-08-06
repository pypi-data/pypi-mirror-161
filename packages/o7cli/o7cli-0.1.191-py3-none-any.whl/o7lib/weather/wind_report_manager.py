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
"""Module the manage the sending fo winf reports to e-mail with correct locations"""


#--------------------------------
#
#--------------------------------
import logging
import typing
import datetime

import boto3

import o7lib.weather.location
import o7lib.weather.wind_report_v2
import o7lib.weather.ca_mf


# create logger
logger = logging.getLogger(__name__)

DB_LOCATIONS = [
    {'code' : 'BDB01' , 'name' : 'Baie de Beauport', 'lon' : -71.1948, 'lat' : 46.8424},
    {'code' : 'BSM01' , 'name' : 'Berthier-sur-Mer', 'lon' : -70.7340515, 'lat' : 46.9357283},
    {'code' : 'NEU01' , 'name' : 'Neuville',         'lon' : -71.5697675, 'lat' : 46.6984466},
    {'code' : 'STA01' , 'name' : 'Sainte-Anne',      'lon' : -70.918802, 'lat' : 47.0239151},
]

DB_FORECAST = [
    {'code' : '002' , 'siteId' : 23000},
    {'code' : '003' , 'siteId' : 23100}
]


DB_CLIENTS = [
    { 'email' : 'philippe.gosselin@hec.ca', 'locations' : 'NEU01,BDB01,BSM01,STA01', 'forecasts' : '003,002'}
]


#*************************************************
#
#*************************************************
class WindReportManager(): # pylint: disable=too-many-instance-attributes
    """Class to manage wind report sending"""

    def __init__(self) -> None:

        # List of locations
        self.locations : typing.Dict[o7lib.weather.location.Location] = {}

        # List of Forecast
        self.forecasts : typing.Dict[dict] = {}

        # list of clients to send a wind report
        self.clients : dict = {}

        self.ses = boto3.client('ses', region_name='ca-central-1')



    #*************************************************
    #
    #*************************************************
    def LoadLocations(self) -> str:
        """Load all locations with latest values"""

        for location in DB_LOCATIONS :

            code = location['code']

            objLocation = o7lib.weather.location.Location(
                lon=location['lon'],
                lat=location['lat'],
                name=location['name'],
            )
            objLocation.LoadAllInfo(days=2)

            self.locations[code] = objLocation

        logger.info(f'LoadLocations: {len(self.locations)} locations loaded')


    #*************************************************
    #
    #*************************************************
    def LoadMarineForecast(self) -> str:
        """Load all locations with latest values"""

        for forecast in DB_FORECAST :

            code = forecast['code']
            siteId = forecast['siteId']

            results = o7lib.weather.ca_mf.GetForecast(siteId=siteId)

            for result in results:
                if result['isExtended'] :
                    self.forecasts[code] = result



        logger.info(f'LoadMarineForecast: {len(self.forecasts)} forecast loaded')



    #*************************************************
    #
    #*************************************************
    def LoadClients(self) -> str:
        """Load all clients that wants a wind report"""

        for client in DB_CLIENTS :

            email = client['email']
            self.clients[email] = {
                'locations' : [],
                'forecasts' : []
            }

            for location in client['locations'].split(','):
                if location in self.locations:
                    self.clients[email]['locations'].append(location)

            for forecast in client['forecasts'].split(','):
                if forecast in self.forecasts:
                    self.clients[email]['forecasts'].append(forecast)


            logger.info(f'LoadClients: {email} with {len(self.clients[email]["locations"])} locations')


    #*************************************************
    #
    #*************************************************
    def ProcessClients(self) -> str:
        """For all client, generate a wind report and send it"""

        for email, params in self.clients.items():

            objsLocations = [ self.locations[location] for location in params['locations'] ]
            objsForecasts = [ self.forecasts[forecast] for forecast in params['forecasts'] ]

            reportObj = o7lib.weather.wind_report_v2.WindReport(
                locations = objsLocations,
                forecasts= objsForecasts
                )
            htmlReport = reportObj.GenerateReportHtml()

            self.SendEmail(email, htmlReport)


    #*************************************************
    #
    #*************************************************
    def SendEmail(self, toEmail, windReport) -> str:
        """Send the email with the HTML report"""

        fromEmail = "windreport@o7conseils.com"

        today = datetime.date.today().isoformat()
        subject = f'Wind Report pour {today}'

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html#SES.Client.send_email
        resp = self.ses.send_email(
            Source=fromEmail,
            Destination={'ToAddresses': [toEmail]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Html': { 'Data': windReport,'Charset': 'UTF-8'} }
            }
        )
        print(f'Sent Email to {toEmail} with subject {subject}')

        print(resp)
        # TODO manager error response




#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    obj = WindReportManager()
    obj.LoadLocations()
    obj.LoadMarineForecast()
    obj.LoadClients()
    obj.ProcessClients()
