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
"""Module allows to view and access EC2 Instances"""


#--------------------------------
#
#--------------------------------
import pprint
import logging
import subprocess

import o7lib.util.input
import o7lib.util.displays
import o7lib.aws.base


logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class Ec2(o7lib.aws.base.Base):
    """Class for EC2 for a Profile & Region"""

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None):
        super().__init__(profile=profile, region=region)
        self.ec2 = self.session.client('ec2')



    #*************************************************
    #
    #*************************************************
    def LoadInstances(self):
        """Load all instances in Region"""

        logger.info('LoadStacks')

        instances = []
        param={}


        done=False
        while not done:

            resp = self.ec2.describe_instances(**param)
            #pprint.pprint(resp)

            if 'NextToken' in resp:
                param['NextToken'] = resp['NextToken']
            else:
                done = True

            logger.info(f'LoadInstances: Number of Reservation found {len(resp["Reservations"])}')
            for reservation in resp['Reservations'] :
                for instance in reservation.get('Instances',[]):

                    stateName = instance['State'].get('Name', 'na')
                    instance['StateName'] = stateName

                    for tag in instance.get('Tags',[]):
                        if tag['Key'] == 'Name':
                            instance['Name'] = tag['Value']
                            break

                    instances.append(instance)


        logger.info(f'LoadInstances: Number of Instances found {len(instances)}')

        return instances



    #*************************************************
    #
    #*************************************************
    def DisplayInstances(self, instances):
        """Diplay Instances"""
        self.ConsoleTitle(left='EC2 Instances')
        print('')
        params = {
            'columns' : [
                {'title' : 'id',          'type': 'i',    'minWidth' : 4  },
                {'title' : 'Name',     'type': 'str',  'dataName': 'Name'},
                {'title' : 'Instance Id', 'type': 'str',  'dataName': 'InstanceId'},
                {'title' : 'Type',        'type': 'str', 'dataName': 'InstanceType'},
                {'title' : 'Launch' ,     'type': 'date',  'dataName': 'LaunchTime'},
                {'title' : 'KeyName',     'type': 'str',  'dataName': 'KeyName'},
                {'title' : 'Private IP',     'type': 'str',  'dataName': 'PrivateIpAddress'},
                {'title' : 'Public IP',     'type': 'str',  'dataName': 'PublicIpAddress'},

                {'title' : 'State'  ,     'type': 'str',  'dataName': 'StateName', 'format' : 'aws-state'},
                {'title' : 'Reason'  ,     'type': 'str',  'dataName': 'StateReason'}



            ]
        }
        o7lib.util.displays.Table(params, instances)

        print('Help: aws ssm start-session --target <instanceId>')



    #*************************************************
    #
    #*************************************************
    def MenuInstances(self):
        """Instances view & edit menu"""

        while True :

            instances = self.LoadInstances()
            self.DisplayInstances(instances)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Open Shell(s) Details(int): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'r':
                    pprint.pprint(instances)
                    o7lib.util.input.WaitInput()

                if key.lower() == 's':
                    iId = o7lib.util.input.InputInt('Enter Instance Id:')
                    if iId and (0 < iId <= len(instances)):
                        cmd = f'aws --profile {self.session.profile_name} --region {self.session.region_name} ssm start-session --target {instances[iId - 1]["InstanceId"]}'
                        print(f'Command: {cmd}')
                        subprocess.call(cmd, shell = True)
                        o7lib.util.input.WaitInput()


            if keyType == 'int' and  0 < key <= len(instances):
                print(f"Printing Raw for instance id: {key}")
                pprint.pprint(instances[key - 1])
                o7lib.util.input.WaitInput()






#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    Ec2().MenuInstances()
