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
"""Module allows to view and access Auto-Scaling Groups"""

#--------------------------------
#
#--------------------------------
import pprint

import logging
import o7lib.util.input
import o7lib.util.displays
import o7lib.aws.base


logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class Asg(o7lib.aws.base.Base):
    """Class for Auto Scaling Groups for a Profile & Region"""

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session = session)
        self.autoscaling = self.session.client('autoscaling')

    #*************************************************
    #
    #*************************************************
    def LoadASGs(self):
        """Returns all Auto-Scaling Groups for this region"""

        logger.info('LoadASGs')

        ret = []
        param={}


        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks
            #print(self.autoscaling.describe_auto_scaling_groups)
            resp = self.autoscaling.describe_auto_scaling_groups(**param)
            #pprint.pprint(resp)

            if 'NextToken' in resp:
                param['NextToken'] = resp['NextToken']
            else: done = True

            asgs = resp.get('AutoScalingGroups',[])
            logger.info(f'LoadASGs: Number of ASG found {len(asgs)}')
            for asg in asgs :

                asg['InstancesCount'] = len(asg.get('Instances',[]))
                ret.append(asg)

        logger.info(f'LoadASGs: Number of Instances found {len(ret)}')

        return ret



    #*************************************************
    #
    #*************************************************
    def DisplayASGs(self, asgs):
        """Displays a summary of ASGs in a Table Format"""

        params = {
            'title' : f"Auto Scaling Groups - {self.TitleLine()}",
            'columns' : [
                {'title' : 'id',          'type': 'i',    'minWidth' : 4  },
                {'title' : 'Name',        'type': 'str',  'dataName': 'AutoScalingGroupName'},
                {'title' : 'Min',         'type': 'str',  'dataName': 'MinSize'},
                {'title' : 'Max',         'type': 'str',  'dataName': 'MaxSize'},
                {'title' : 'Desired' ,     'type': 'str', 'dataName': 'DesiredCapacity'},
                {'title' : 'Instances' ,     'type': 'str', 'dataName': 'InstancesCount'},


                {'title' : 'Status'  ,     'type': 'str',  'dataName': 'Status', 'format' : 'aws-state'}


            ]
        }
        o7lib.util.displays.Table(params, asgs)

    #*************************************************
    #
    #*************************************************
    def MenuAutoScalingGroups(self):
        """Menu to view and edit all ASGs in current region"""

        while True :

            asgs = self.LoadASGs()
            self.DisplayASGs(asgs)
            keyType, key = o7lib.util.input.InputMulti('Option -> Exit(e) Raw(r) Details(int): ')

            if keyType == 'str':
                if key.lower() == 'e':
                    break
                if key.lower() == 'r':
                    pprint.pprint(asgs)
                    o7lib.util.input.WaitInput()

            if keyType == 'int' and key > 0 and key <= len(asgs):
                print(f"Printing Raw for asg id: {key}")
                pprint.pprint(asgs[key - 1])



#*************************************************
# For Quick Testing
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    Asg().MenuAutoScalingGroups()
