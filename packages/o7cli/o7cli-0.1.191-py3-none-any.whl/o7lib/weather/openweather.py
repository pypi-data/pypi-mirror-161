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
"""
Module to access Open Weather Map available information

Required Environment Variable:
OPENWM_APIKEY=<Client API Key, see https://api.openweathermap.org>

"""

#--------------------------------
#
#--------------------------------
import os
import logging
import datetime
import pprint
import pytz
import requests

import o7lib.util.conversion

tzEastern = pytz.timezone('US/Eastern')


#*************************************************
#
# https://openweathermap.org/api/hourly-forecast
#
#*************************************************
URL_API = 'https://api.openweathermap.org'

# create logger
logger = logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class OpenWmApi():
    """Class to get data from the Open Weather API"""

    #*************************************************
    #
    #*************************************************
    def __init__(self):

        self.apiKey = os.environ.get('OPENWM_APIKEY', None)

        if self.apiKey is None:
            logger.critical('OPENWM_APIKEY not found, please add required env variable')


    #*************************************************
    # https://openweathermap.org/api/one-call-api#parameter
    #*************************************************
    def GetOneCall(self, lon, lat):
        """Return data from the One Call entry point for a lon-lat"""

        logger.debug(f'Requesting Data for lon:{lon} lat:{lat}')

        params = {
                'appid' : self.apiKey,
                'lon' : lon,
                'lat' : lat,
                'units': 'metric',
        }

        url = URL_API + '/data/2.5/onecall'
        response = requests.get(url=url, params=params)

        if response.status_code != 200 :
            logger.warning(f'Got Error Status Code: {response.status_code}')
            logger.warning(f'Error Message: {response.text}')
            return None

        data = response.json()
        logger.debug(f'Sucessful response: {response.status_code}')

        return data


    #*************************************************
    #
    #*************************************************
    def GetHourlyForecast(self, lon, lat):
        """Return list of hourly forecast"""

        logger.info(f'GetHourlyForecast: Requesting Foracast for lon:{lon} lat:{lat}')

        data = self.GetOneCall(lon, lat)
        if data is None:
            return None

        if 'hourly' not in data:
            logger.warning('No Hourly data found')
            logger.warning(f'rx data {data}')
            return None

        ret = []

        logger.info(f'GetHourlyForecast: Number of Hourly Forecast = {len(data["hourly"])}')

        for hour in data['hourly']:
            utcTime = datetime.datetime.fromtimestamp(hour['dt']).astimezone(tz=pytz.utc)
            eastTime = tzEastern.normalize(utcTime)


            rec = {
                'dtu' : utcTime.isoformat(),
                'dtl' : eastTime.isoformat(),
                'temp' : hour['temp'],
                'wind' : o7lib.util.conversion.SpeedMsToKnot(hour['wind_speed']),
                'gust' : o7lib.util.conversion.SpeedMsToKnot(hour['wind_gust']),
                'deg' : hour['wind_deg']
            }
            #pprint.pprint(rec)
            ret.append(rec)

        return ret


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    #theData = GetOneCall(-71.1948, 46.8424)
    #pprint.pprint(theData)


    theDatasets = OpenWmApi().GetHourlyForecast(-71.1948, 46.8424)
    pprint.pprint(theDatasets)
