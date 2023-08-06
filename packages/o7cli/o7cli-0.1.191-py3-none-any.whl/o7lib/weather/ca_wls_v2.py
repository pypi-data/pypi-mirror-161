"""Module to Interface with the Canadian Water Level Service Version 2"""
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


import pprint
import math
import logging
import datetime
import typing

# https://docs.python-requests.org/en/master/
import requests
import pandas as pd

logger=logging.getLogger(__name__)

#*************************************************
#  Canadian Water Level Service
#
# https://tides.gc.ca/en/web-services-offered-canadian-hydrographic-service
# SWagger https://api-iwls.dfo-mpo.gc.ca/swagger-ui/index.html?configUrl=/v3/api-docs/swagger-config
# Get all Stations: https://api-iwls.dfo-mpo.gc.ca/api/v1/stations
#
# {"
#   id":"5cebf1e23d0f4a073c4bc0f6",
#   "code":"03248",
#   "officialName":"Vieux-Québec",
#   "operating":true,
#   "latitude":46.811111,"longitude":-71.201944,
#   "type":"PERMANENT",
#   "timeSeries":[
#       {"id":"5cebf1e23d0f4a073c4bc0e1","code":"wlo",
#       "nameEn":"Water level official value",
#       "nameFr":"Niveau d'eau, valeur officielle",
#        "phenomenonId":"5ce598df487b84486892821c"},
#      {"id":"5cebf1e23d0f4a073c4bc0ea","code":"wlp",
#       ...
# ************************************************
URL_WLS = 'https://api-iwls.dfo-mpo.gc.ca'

# approximate radius of earth in km
EARTH_RADIUS = 6373.0


def LonLatDistane(lon1, lat1, lon2, lat2) -> float:
    """Measure the distance between 2 geo point"""

    rLon1 = math.radians(lon1)
    rLat1 = math.radians(lat1)
    rLon2 = math.radians(lon2)
    rLat2 = math.radians(lat2)

    dLon = rLon2 - rLon1
    dLat = rLat2 - rLat1

    arc = math.sin(dLat / 2)**2 + math.cos(rLat1) * math.cos(rLat2) * math.sin(dLon / 2)**2
    curve = 2 * math.atan2(math.sqrt(arc), math.sqrt(1 - arc))

    return EARTH_RADIUS * curve


class WaterTemperature(typing.NamedTuple):
    """Tuple to store water temp and time of measure"""
    value: float
    dtu: datetime.datetime

class StationInfo(typing.NamedTuple):
    """Station Information"""
    id: str
    name: str
    url: str = ''
    distance: float = 0

#*************************************************
#
#*************************************************
class CaWaterLevelService():
    """Class to inteface with the Canadian Water Level Service"""

    #*************************************************
    #
    #*************************************************
    def __init__(self) -> None:

        self.url = URL_WLS
        self.stations : pd.DataFrame = None


    #*************************************************
    #
    #*************************************************
    def GetInfo(self, stationId : str, distance: float = 0.0) -> StationInfo:
        """Get Station Information """

        station = self.stations.loc[stationId]

        # print(station)

        info = StationInfo(
            id=stationId,
            name=station['officialName'],
            url=f'https://tides.gc.ca/fr/stations/{station["code"]}',
            distance=distance
        )

        return info


    #*************************************************
    #
    #*************************************************
    def LoadAllStation(self):
        """Get all possible station"""

        url = self.url + '/api/v1/stations'
        logger.info(f'LoadAllStation: Requesting URL -> {url}')

        resp = requests.get(url)
        if resp.status_code >= 300 :
            logger.error(f'LoadAllStation: Bad HTTP Status code: {resp.status_code} Error: {resp.json()}')
            resp.raise_for_status()


        df = pd.DataFrame(data=resp.json())
        logger.info(f'LoadAllStation: Number of station received: {len(df.index)}' )

        # Remove discontinued stations
        df = df[~df['type'].isin(['DISCONTINUED', 'UNKNOWN'])]

        # Build lookup array for available timeseries
        df['ts'] = df['timeSeries'].apply(lambda x: [ts['code'] for ts in x ])

        # Set index
        df.set_index(keys='id', drop=True, inplace=True)

        self.stations = df
        logger.info(f'LoadAllStation: Number of operating station: {len(self.stations.index)}' )
        return len(self.stations.index)


    #*************************************************
    #
    #*************************************************
    def _StationsReady(self):
        """Verify if stations are loaded, if not load is requested"""
        if self.stations is None:
            self.LoadAllStation()

    #*************************************************
    #
    #*************************************************
    def _GetSerie(self, stationId : str, days : int = 3, serie : str = 'wlp') -> pd.Series:
        """Get the Raw Data for a Specific Data Serie"""

        logger.debug(f'_GetSerie: -> id={stationId}; days={days} serie={serie}')
        url = self.url + f'/api/v1/stations/{stationId}/data'

        # ------------------------------
        # Calculate time rage ( from - to )
        # ------------------------------
        now = datetime.datetime.utcnow()
        dtFrom = dtTo = now.isoformat("T", "seconds") + 'Z'

        if days >= 0 :
            dtTo = (now + datetime.timedelta(days=days)).isoformat("T", "seconds") + 'Z'
        else:
            days = abs(days)
            dtFrom = (now - datetime.timedelta(days=days)).isoformat("T", "seconds") + 'Z'

        ret = []

        params = {
            "time-series-code" : serie,
            "from" : dtFrom,
            "to" : dtTo,
        }

        #pprint.pprint(params)
        resp = requests.get(url,params=params)
        if resp.status_code >= 300 :
            logger.warning(f'_GetSerie: Bad HTTP Status code: {resp.status_code} Error: {resp.json()}')
            resp.raise_for_status()

        datas = resp.json()
        logger.debug(f'_GetSerie: Number of data point received: {len(datas)}' )

        dfData = pd.DataFrame(data=datas)
        dfData['eventDate'] = pd.to_datetime(dfData['eventDate'])
        dfData.set_index(keys='eventDate', drop = True, inplace=True)

        ret = dfData['value']
        return ret



    #*************************************************
    #
    #*************************************************
    def GetClosestStation(self, lon : float, lat: float, withTs : str = None) -> StationInfo:
        """Get the id of the closest station and the distance in KM"""

        self._StationsReady()
        logger.info(f'GetClosestStation: lon={lon} lat={lat} withTs={withTs}')

        foundId = None
        foundDist = -1

        # Get station with only the TS we want
        if withTs is None:
            df = self.stations
        else:
            df = self.stations[self.stations['ts'].astype(str).str.contains(withTs)]

        if len(df) < 1 :
            logger.error(f'GetClosestStation: No Station found with Time Serie : {withTs}')
            return None, None

        dist = df.apply(lambda x: LonLatDistane(lon1 = x['longitude'], lat1 = x['latitude'], lon2=lon, lat2=lat), axis=1).sort_values()

        # print(dist[0:10])

        foundId = dist.index[0]
        foundDist = dist[0]
        logger.info(f'GetClosestStation: found {self.stations.loc[foundId]["officialName"]} at {foundDist:.2f} km ')

        return self.GetInfo(foundId, foundDist)


    #*************************************************
    #
    #*************************************************
    def GetLastWaterTemp(self, stationId : str) -> WaterTemperature:
        """Get the last measured temperature"""

        logger.info(f'GetLastTemperature: id={stationId}')

        stationTs = self.stations.loc[stationId]['ts']
        serie = None

        if 'wt1' in stationTs :
            serie = 'wt1'
        elif 'wt2' in stationTs :
            serie = 'wt2'
        else :
            logger.info('GetLastWaterTemp: No Water Temperature Serie Available')
            return None


        temps = self._GetSerie(stationId, days=-1, serie=serie)
        ret = None


        if len(temps.index) > 0 :
            ret = WaterTemperature(temps.iloc[0], temps.index[0])
            logger.info(f'GetLastTemperature: Found -> {ret}' )

        return ret


    #*************************************************
    #
    #*************************************************
    def GetWlpHourly(self, stationId : str, days : int = 3) -> pd.DataFrame:
        """Get the hourly forecast of tides (height + minutes of hilo)"""

        logger.info(f'GetTidesHiLo: stationId={stationId} days={days}')

        dfWlp =  self._GetSerie(stationId=stationId, serie='wlp', days=days)
        dfHilo = self._GetSerie(stationId=stationId, serie='wlp-hilo', days=days)

        # Every Hours, remove first row
        dfWlpH = dfWlp.resample(rule='1H', label='left').first()[1:]

        # Keep minutes of the Hi/Lo tide
        dfHiloH = pd.Series(data=dfHilo.index, index=dfHilo.index).dt.minute
        dfHiloH = dfHiloH.resample(rule='1H', label='left').first()

        ret = pd.DataFrame()
        ret['height'] = dfWlpH
        ret['hilo'] = dfHiloH

        return ret


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.min_rows', 30)

    theObj = CaWaterLevelService()
    theObj.LoadAllStation()

    # # Distance
    # dfStations['dist'] = dfStations.apply(lambda x: LonLatDistane(lon1 = x['longitude'], lat1 = x['latitude'], lon2=-70.7340515, lat2=46.9357283 ), axis=1)
    # dfStations = dfStations.sort_values(by = 'dist')

    print(theObj.stations[['officialName','type' ,'operating', 'longitude', 'latitude', 'ts']][0:50])
    print(theObj.stations.info())

    baieInfo = theObj.GetClosestStation(lon=-71.1948, lat=46.8424)

    print(baieInfo)


    # idBerthier = theObj.GetClosestStation(lon=-70.7340515, lat=46.9357283)
    # #pprint.pprint(theObj.stations[idBerthier])

    # print(theObj.GetInfo(idBerthier))


    # dfBaie = theObj.GetWlpHourly(stationId=idBaie, days=3)
    # print(dfBaie.iloc[0:30])


    # dfBerthier = theObj.GetTidesHourly(stationId=idBerthier, days=3)

    # dfFinal = dfBaie.merge(right=dfBerthier, how='outer', suffixes=('_baie','_berthier'), left_index=True, right_index=True)

    # print(dfFinal.iloc[0:100])

    #temp = theObj.GetLastTemperature(stationId=idBaie)
    #print(temp)
    #GetLastTemperature("5cebf1e23d0f4a073c4bc0f6")
