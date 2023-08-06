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
import logging
import pprint
import o7lib.util.input
import o7lib.util.displays
import o7lib.aws.base


logger=logging.getLogger(__name__)

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/servicediscovery.html

#*************************************************
#
#*************************************************
class CloudMap(o7lib.aws.base.Base):
    """Class to get Cloud Map Details"""

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session = session)
        self.sd = self.session.client('servicediscovery')

        self.namespaceId = None
        self.serviceId = None

    #*************************************************
    #
    #*************************************************
    def LoadNamespaces(self):

        logger.info('LoadNamespaces')

        nss = []
        param={}


        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks
            resp = self.sd.list_namespaces(**param)
            #pprint.pprint(resp)

            if 'NextToken' in resp: param['NextToken'] = resp['NextToken']
            else: done = True

            logger.info(f'LoadNamespaces: Number of Namespace found {len(resp["Namespaces"])}')
            for ns in resp['Namespaces'] :
                nss.append(ns)

        return nss

    #*************************************************
    #
    #*************************************************
    def LoadServices(self, nsId):

        logger.info('LoadServices')

        services = []
        param={
            'Filters' : [{
                'Name' : 'NAMESPACE_ID',
                'Values': [nsId],
                'Condition': 'EQ'
            }]
        }


        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks
            resp = self.sd.list_services(**param)
            #pprint.pprint(resp)

            if 'NextToken' in resp: param['NextToken'] = resp['NextToken']
            else: done = True

            logger.info(f'LoadServices: Number of Services found {len(resp["Services"])}')
            for s in resp['Services'] :

                services.append(s)

        return services

    #*************************************************
    #
    #*************************************************
    def LoadInstances(self):

        logger.info('LoadInstances')

        instances = []
        param={
            'ServiceId' : self.serviceId
        }


        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks
            resp = self.sd.list_instances(**param)
            #pprint.pprint(resp)

            if 'NextToken' in resp: param['NextToken'] = resp['NextToken']
            else: done = True

            logger.info(f'LoadInstances: Number of Instances found {len(resp["Instances"])}')
            for i in resp['Instances'] :
                instances.append(i)

        return instances


    #*************************************************
    #
    #*************************************************
    def DeregisterInstance(self, instanceId):

        logger.info(f'DeregisterInstances: Instance Id:{instanceId}')
        logger.info('DeregisterInstances: TBD')

        return

    #*************************************************
    #
    #*************************************************
    def DisplayNamespaces(self, nss):

        params = {
            'title' : f"Namespaces - {self.TitleLine()}",
            'columns' : [
                {'title' : 'id',          'type': 'i',    'minWidth' : 4  },
                {'title' : 'Name',        'type': 'str',  'dataName': 'Name'},
                {'title' : 'Type',        'type': 'str', 'dataName':'Type'},
                {'title' : 'ID',          'type': 'str',   'dataName':'Id'},
                {'title' : 'Description', 'type': 'str',   'dataName':'Description'}
            ]
        }
        o7lib.util.displays.Table(params, nss)

        return

    #*************************************************
    #
    #*************************************************
    def DisplayServices(self, services):

        params = {
            'title' : f"Services - {self.TitleLine()}",
            'columns' : [
                {'title' : 'id',          'type': 'i',    'minWidth' : 4  },
                {'title' : 'Name',        'type': 'str',  'dataName': 'Name'},
                {'title' : 'Type',        'type': 'str', 'dataName':'Type'},
                {'title' : 'ID',          'type': 'str',   'dataName':'Id'},
                {'title' : 'Description', 'type': 'str',   'dataName':'Description'}
            ]
        }
        o7lib.util.displays.Table(params, services)

        return

    #*************************************************
    #
    #*************************************************
    def DisplayInstances(self, instances):

        params = {
            'title' : f"Instances for Service ID : {self.serviceId}",
            'columns' : [
                {'title' : '',           'type': 'i',    'minWidth' : 4  },
                {'title' : 'ID',          'type': 'str',   'dataName':'Id'},
                {'title' : 'Attributes', 'type': 'str',   'dataName':'Attributes'}
            ]
        }
        o7lib.util.displays.Table(params, instances)

        return


    #*************************************************
    #
    #*************************************************
    def MenuInstances(self):

        while True :

            instances = self.LoadInstances()
            self.DisplayInstances(instances)
            t, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Deregister(d) Details(int): ')

            if t == 'str':
                if key.lower() == 'b': break
                if key.lower() == 'r': pprint.pprint(instances); o7lib.util.input.WaitInput()
                if key.lower() == 'd':
                    id = o7lib.util.input.InputInt('Instance to Deregister ?')
                    if id > 0 and id <= len(instances) and o7lib.util.input.IsItOk(f'Confirm you want to Deregister {instances[id - 1]["Id"]}'):
                        self.DeregisterInstance(instances[id - 1]['Id'])


            if t == 'int' and key > 0 and key <= len(instances):
                print(f"Printing Raw for Services id: {key}")
                pprint.pprint(instances[key - 1])

    #*************************************************
    #
    #*************************************************
    def MenuServices(self, nsId):

        while True :

            services = self.LoadServices(nsId)
            self.DisplayServices(services)
            t, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Details(int): ')

            if t == 'str':
                if key.lower() == 'b': break
                if key.lower() == 'r': pprint.pprint(services); o7lib.util.input.WaitInput()

            if t == 'int' and key > 0 and key <= len(services):
                self.serviceId = services[key - 1]['Id']
                self.MenuInstances()


    #*************************************************
    #
    #*************************************************
    def MenuNamespaces(self):

        while True :

            nss = self.LoadNamespaces()
            self.DisplayNamespaces(nss)
            t, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Details(int): ')

            if t == 'str':
                if key.lower() == 'b': break
                if key.lower() == 'r': pprint.pprint(nss); o7lib.util.input.WaitInput()

            if t == 'int' and key > 0 and key <= len(nss):
                self.MenuServices(nss[key - 1]['Id'])



#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    CloudMap().MenuNamespaces()


