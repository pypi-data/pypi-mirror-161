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
"""Module to access NOAA available information"""


#--------------------------------
#
#--------------------------------
# https://docs.python-requests.org/en/master/
import pprint
import os
import logging
import configparser
import requests


#*************************************************
#
# https://www.ncdc.noaa.gov/cdo-web/webservices/v2
#
#*************************************************
URL_API_V2 = 'https://www.ncdc.noaa.gov/cdo-web/api/v2'

# create logger
logger = logging.getLogger(__name__)

# https://docs.python.org/3/library/configparser.html


#*************************************************
#
#*************************************************
class NoaaApiV2():
    """Class to get data from the NOAA API"""

    #*************************************************
    #
    #*************************************************
    def __init__(self, token = None):

        self.token = token

        if token is None:
            self.token = os.environ.get('NOAAV2_TOKEN', None)

        if self.token is None:
            logger.critical('NOAAV2_TOKEN not found, please add required env variable')

        # self.LoadConfig()

    #*************************************************
    #
    #*************************************************
    def LoadConfig(self):
        """Read Config File"""

        config = configparser.ConfigParser()
        config.read('o7cli.ini')

        logger.info(f'LoadConfig - Found Sections : {config.sections()}')

        if self.__module__ not in config:
            config[self.__module__] = {}


        noaa = config[self.__module__]
        self.token = noaa.get('token', fallback=None)

        if self.token is None:
            noaa['token'] = 'Copy token here <https://www.ncdc.noaa.gov/cdo-web/webservices/v2>'
            with open('o7cli.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)


    #*************************************************
    # https://www.ncdc.noaa.gov/cdo-web/webservices/v2#datasets
    #*************************************************
    def GetAllDatasets(self):
        """Returns all available datasets"""

        logger.info('GetAllDatasets')

        ret = []
        params = {
            'limit' : 100,
            'offset' : 1
        }

        url = URL_API_V2 + '/datasets'
        response = requests.get(url=url, headers={"token":self.token}, params=params)

        if response.status_code >= 300 :
            logger.error(f'GetAllDatasets - Response Status Code={response.status_code} text={response.text}')
            return None

        jResponse = response.json()

        if 'results' not in jResponse:
            logger.error(f'GetAllDatasets - Error with GET: {jResponse}')
            return None

        logger.debug(f'GetAllDatasets - Rx metadata : {jResponse["metadata"]}')

        ret += jResponse['results']

        logger.info(f'GetAllStation - Number of datasets received: {len(ret)}' )


        return ret


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    theDatasets = NoaaApiV2().GetAllDatasets()
    pprint.pprint(theDatasets)
