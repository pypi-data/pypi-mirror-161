"""Module Compile the weather data for a single location"""
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


import logging

import pandas as pd

import o7lib.weather.ca_wls_v2
import o7lib.weather.openweather

logger=logging.getLogger(__name__)


caWls =  o7lib.weather.ca_wls_v2.CaWaterLevelService()

#*************************************************
#
#*************************************************
class Location(): # pylint: disable=too-many-instance-attributes
    """Class to compile weather data for a single location"""

    #*************************************************
    #
    #*************************************************
    def __init__(self, lon : int, lat : int, name : str = '') -> None:

        self.lon = lon
        self.lat = lat
        self.name : str = name

        self.stationWlp : o7lib.weather.ca_wls_v2.StationInfo = None
        self.stationWt : o7lib.weather.ca_wls_v2.StationInfo = None


        # http://maps.google.com/maps/place/<name>/@<lat>,<long>,15z/data=<mode-value>
        # https://developers.google.com/maps/documentation/urls/get-started
        # self.gmapUrl = f'https://www.google.ca/maps/@{self.lat},{self.lon},15z'
        self.gmapUrl = f'http://maps.google.com/maps/place/{self.name}/@{self.lat},{self.lon},15z'


        self.lastWaterTemp : o7lib.weather.ca_wls_v2.WaterTemperature = None
        self.hourlyForecast: pd.DataFrame = None

        self.InitWlsStation()

    #*************************************************
    #
    #*************************************************
    def __str__(self) -> str:
        return f'Location [{self.name}] at lon/lat {self.lon}/{self.lat}'

    #*************************************************
    #
    #*************************************************
    def InitWlsStation (self):
        """Find the closest Water Level Service Station"""

        self.stationWlp = caWls.GetClosestStation(lon = self.lon, lat = self.lat, withTs='wlp')
        self.stationWt = caWls.GetClosestStation (lon = self.lon, lat = self.lat, withTs='wt')

    #*************************************************
    #
    #*************************************************
    def PrintDetails(self):
        """Print details for this location"""

        print('-' * 50)
        print(f'Station Name (Lon / Lat): {self.name} ({self.lon} / {self.lat})')
        print('')
        print(f'Closest Water Level Station : {self.stationWlp.name} at {self.stationWlp.distance:.2f}km')
        print(f'Closest Water Temperature Station : {self.stationWt.name} at {self.stationWt.distance:.2f}km')
        print('')

        if self.lastWaterTemp is not None:
            print(f'Latest Water Temp: {self.lastWaterTemp.value}C (updated at {self.lastWaterTemp.dtu.isoformat()})')

        if self.hourlyForecast is not None:
            print(f'Number of hourly forecast: {len(self.hourlyForecast.index)}')
        print('-' * 50)


    #*************************************************
    #
    #*************************************************
    def LoadAllInfo(self, days : int = 3):
        """Load all weather related details for this location"""

        self.LoadHourlyForecast(days=days)
        self.LoadLastWaterTemp()


    #*************************************************
    #
    #*************************************************
    def LoadHourlyForecast(self, days : int = 3):
        """Get Hourly Forcast for thsi location (tide, wind & temperature)"""

        dfTides = caWls.GetWlpHourly(stationId=self.stationWlp.id, days=days)
        winds = o7lib.weather.openweather.OpenWmApi().GetHourlyForecast(lon=self.lon, lat=self.lat)

        if winds is not None:
            dfWind = pd.DataFrame(data=winds)
            dfWind['dtu'] = pd.to_datetime(dfWind['dtu'])
            dfWind = dfWind.set_index(keys='dtu', drop = True)
            dfWind.drop(columns=['dtl'], inplace=True)
            dfWind = dfWind.resample(rule='1H', label='left').first()[1:]
        else:
            dfWind = pd.DataFrame(columns=['wind', 'gust', 'deg'])

        dfRet = dfTides.merge(right=dfWind, how='outer', left_index=True, right_index=True)

        self.hourlyForecast = dfRet
        return dfRet


    #*************************************************
    #
    #*************************************************
    def LoadLastWaterTemp(self) -> o7lib.weather.ca_wls_v2.WaterTemperature:
        """Get the latest water temperature"""

        self.lastWaterTemp = caWls.GetLastWaterTemp(stationId = self.stationWt.id)
        return self.lastWaterTemp


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    # pd.set_option('display.max_rows', 50)
    # pd.set_option('display.min_rows', 30)

    baieLon = -71.1948
    baieLat = 46.8424
    berthierLon = -70.7340515
    berthierLat = 46.9357283

    # neuvilleLon = -71.5697675
    # neuvilleLat = 46.6984466


    baieObj = Location(lon=baieLon, lat=baieLat, name='Baie de Beauport')
    # berthierObj = Location(lon=berthierLon, lat=berthierLat, name='Berthier sur Mer')
    # neuvilleObj = Location(lon=neuvilleLon, lat=neuvilleLat, name='Neuville')

    #dfBaie = baieObj.LoadHourlyForecast(days=2)
    # # dfBerthier = berthierObj.LoadHourlyForecast(days=2)

    # # dfFinal = dfBaie.merge(right=dfBerthier, how='outer', suffixes=('_baie','_berthier'), left_index=True, right_index=True)

    baieObj.LoadAllInfo(days=2)
    baieObj.PrintDetails()

    print(baieObj.hourlyForecast[0:10])
    # print(berthierObj)
    # print(neuvilleObj)

    # theObj.GetLastTemperature(stationId=theId)
    #GetLastTemperature("5cebf1e23d0f4a073c4bc0f6")
