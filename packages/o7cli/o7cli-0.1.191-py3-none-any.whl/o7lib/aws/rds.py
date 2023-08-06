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


#--------------------------------
#
#--------------------------------
import pprint
import datetime
import logging

import o7lib.util.input
import o7lib.util.displays
import o7lib.aws.base


logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class Rds(o7lib.aws.base.Base):

    #  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html#rds

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None):
        super().__init__(profile=profile, region=region)
        self.rds = self.session.client('rds')



    #*************************************************
    #
    #*************************************************
    def LoadInstances(self):

        logger.info('LoadInstances')

        instances = []
        param={}

        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html#RDS.Client.describe_db_instances
            resp = self.rds.describe_db_instances(**param)
            #pprint.pprint(resp)

            if 'Marker' in resp:
                param['Marker'] = resp['Marker']
            else: done = True

            logger.info('LoadInstances: Number of DBInstances found %d', len(resp["DBInstances"]))
            for dbI in resp['DBInstances'] :
                instances.append(dbI)

        return instances


    #*************************************************
    #
    #*************************************************
    def LoadCpuUtilization(self, instanceId):

        cloudwatch = self.session.resource('cloudwatch')
        metric = cloudwatch.Metric('AWS/RDS','CPUUtilization')
        metric.load()

        resp = metric.get_available_subresources()
        pprint.pprint(resp)

        end = datetime.datetime.utcnow()
        start =  end - datetime.timedelta(days=5)


        param = {
            'Dimensions' : [{'Name': 'DBInstanceIdentifier', 'Value': instanceId}],
            'Statistics' : ['Average', 'Minimum', 'Maximum'],
            'StartTime' : start,
            'EndTime' : end,
            'Period' : 3600 * 24
        }


        logger.info('LoadCpuUtilization: param: %s', param)

        resp = metric.get_statistics(**param)

        pprint.pprint(resp)

        dataPoint = resp.get('Datapoints',[])


        tableParams = {
            'title' : f"DB CPU Utilization for {instanceId}",
            'columns' : [
                {'title' : 'Date / Time',    'type': 'datetime', 'dataName': 'Timestamp'},
                {'title' : 'Average',        'type': 'str',      'dataName': 'Average'},
                {'title' : 'Maximum',         'type': 'str',      'dataName': 'Maximum'},


            ]
        }
        o7lib.util.displays.Table(tableParams, dataPoint)




    #*************************************************
    #
    #*************************************************
    def DisplayInstances(self, stacks):

        params = {
            'title' : f"EC2 Instances - {self.TitleLine()}",
            'columns' : [
                {'title' : 'id',             'type': 'i',    'minWidth' : 4  },
                {'title' : 'Instance Id',    'type': 'str',  'dataName': 'DBInstanceIdentifier'},
                {'title' : 'DB Name',        'type': 'str',     'dataName': 'DBName'},
                {'title' : 'Class',          'type': 'str', 'dataName': 'DBInstanceClass'},
                {'title' : 'Engine Version' ,'type': 'str',  'dataName': 'EngineVersion'},
                {'title' : 'AZ',             'type': 'str', 'dataName': 'AvailabilityZone'},
                {'title' : 'Multi-AZ',       'type': 'str',  'dataName': 'MultiAZ'},
                # {'title' : 'Private IP',     'type': 'str',  'dataName': 'PrivateIpAddress'},
                # {'title' : 'Public IP',     'type': 'str',  'dataName': 'PublicIpAddress'},

                # {'title' : 'State'  ,     'type': 'str',  'dataName': 'StateName', 'format' : 'aws-state'},
                # {'title' : 'Reason'  ,     'type': 'str',  'dataName': 'StateReason'}


            ]
        }
        o7lib.util.displays.Table(params, stacks)


        return


    #*************************************************
    #
    #*************************************************
    def MenuInstances(self):

        while True :

            instances = self.LoadInstances()
            self.DisplayInstances(instances)
            typ, key = o7lib.util.input.InputMulti('Option -> Exit(e) Raw(r) Details(int): ')

            if typ == 'str':
                if key.lower() == 'e':
                    break
                if key.lower() == 'r':
                    pprint.pprint(instances)
                    o7lib.util.input.WaitInput()

            if typ == 'int' and  0 < key <= len(instances):
                print(f"Printing Raw for DB instance id: {key}")
                pprint.pprint(instances[key - 1])


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    Rds().MenuInstances()
