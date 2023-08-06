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
Module to access Planet OI available information

Required Environment Variable:
PLANETOS_APIKEY=<Client API Key, see http://docs.planetos.com/#rest-api-v1>

"""

#--------------------------------
#
#--------------------------------
import os
import pprint
import logging
import datetime
import pytz
import requests
import o7lib.util.conversion

#*************************************************
#
# http://docs.planetos.com/#authentication
# https://data.planetos.com/datasets/noaa_nam_awips_phys
# https://data.planetos.com/datasets/noaa_nam_awips_12
# https://data.planetos.com/datasets/noaa_gfs_global_sflux_0.12d

# Conver u v wind component to wind speed & degre
# https://confluence.ecmwf.int/pages/viewpage.action?pageId=133262398
#*************************************************

TZ_EASTERN = pytz.timezone('US/Eastern')
URL_API = 'https://api.planetos.com'

# create logger
logger = logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class PlanetOsApi():
    """Class to get data from the Planet OS API"""

    #*************************************************
    #
    #*************************************************
    def __init__(self):

        self.apiKey = os.environ.get('PLANETOS_APIKEY', None)
        if self.apiKey is None:
            logger.critical('PLANETOS_APIKEY not found, please add required env variable')


    #*************************************************
    #
    #*************************************************
    def GetPoints(self, dataset, lon, lat, context=None ):
        """Returns data point for a datase at a specific lon-lat"""

        logger.debug(f'Requesting points for dataset {dataset} for lon:{lon} lat:{lat}')

        params = {
                'apikey' : self.apiKey,
                'lon' : lon,
                'lat' : lat,
                'count' : 255
        }

        if context is not None:
            params['context'] = context

        url = URL_API + f'/v1/datasets/{dataset}/point'
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
    def GetNamWindAboveGround5(self, lon, lat):
        """Returns wind (Nam - Wind Above Ground 5) data for a specific lon-lat"""

        logger.debug(f'Requesting Foracast for lon:{lon} lat:{lat}')

        data = self.GetPoints(dataset='noaa_nam_awips_phys', lon=lon, lat=lat, context='reftime_time1_height_above_ground5_lat_lon')
        if data is None:
            return None

        if 'entries' not in data:
            logger.warning('No Entries data found')
            logger.info(f'rx data -> {data}')
            return None

        ret = []

        logger.debug(f'Number of Hourly Forecast :{len(data["entries"])}')

        for entry in data['entries']:
            utcTime = datetime.datetime.fromisoformat(entry['axes']['time']).astimezone(tz=pytz.utc)
            eastTime = TZ_EASTERN.normalize(utcTime)

            windU = entry['data']['U_Component_of_Hourly_Maximum_10m_Wind_Speed_height_above_ground_1_Hour_Maximum']
            windV = entry['data']['U_Component_of_Hourly_Maximum_10m_Wind_Speed_height_above_ground_1_Hour_Maximum']
            wind = o7lib.util.conversion.SpeedUVToWs(windU,windV)
            deg = o7lib.util.conversion.DirectionUVToDeg(windU,windV)

            rec = {
                'dtu' : utcTime.isoformat(),
                'dtl' : eastTime.isoformat(),
                'wind' : o7lib.util.conversion.SpeedMsToKnot(wind),
                'deg' : deg
            }
            #pprint.pprint(rec)
            ret.append(rec)

        return ret


    #*************************************************
    #
    #*************************************************
    def GetNamWindAboveGround3(self, lon, lat):
        """Returns wind (Nam - Wind Above Ground 3) data for a specific lon-lat"""

        logger.debug(f'Requesting Foracast for lon:{lon} lat:{lat}')

        data = self.GetPoints(dataset='noaa_nam_awips_phys', lon=lon, lat=lat, context='reftime_time_height_above_ground3_lat_lon')
        if data is None:
            return None

        if 'entries' not in data:
            logger.warning('No Entries data found')
            logger.info(f'rx data -> {data}')
            return None

        ret = []

        logger.debug(f'Number of Hourly Forecast :{len(data["entries"])}')

        for entry in data['entries']:
            utcTime = datetime.datetime.fromisoformat(entry['axes']['time']).astimezone(tz=pytz.utc)
            eastTime = TZ_EASTERN.normalize(utcTime)

            windU = entry['data']['u-component_of_wind_height_above_ground']
            windV = entry['data']['v-component_of_wind_height_above_ground']
            wind = o7lib.util.conversion.SpeedUVToWs(windU,windV)
            deg = o7lib.util.conversion.DirectionUVToDeg(windU,windV)

            rec = {
                'dtu' : utcTime.isoformat(),
                'dtl' : eastTime.isoformat(),
                'wind' : o7lib.util.conversion.SpeedMsToKnot(wind),
                'deg' : deg
            }
            #pprint.pprint(rec)
            ret.append(rec)

        return ret


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    # theData = GetPoints(dataset='noaa_nam_awips_phys', lon=-71.1948, lat=46.8424, context='reftime_time_height_above_ground3_lat_lon')
    # pprint.pprint(theData)


    # theDatasets = GetNamWindAboveGround5(-71.1948, 46.8424)
    # pprint.pprint(theDatasets)

    theDatasets = PlanetOsApi().GetNamWindAboveGround3(-71.1948, 46.8424)
    pprint.pprint(theDatasets)
