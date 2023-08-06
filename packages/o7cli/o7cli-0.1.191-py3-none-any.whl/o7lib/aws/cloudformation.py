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
"""Module allows to view and access Cloud Formation"""

#--------------------------------
#
#--------------------------------
import datetime
import logging
import os
import pprint

import botocore
import botocore.config

import o7lib.util.input
import o7lib.util.file_explorer
import o7lib.aws.base
import o7lib.util.displays as o7d
import o7lib.util.terminal as o7t
import o7lib.util.table
import o7lib.aws.s3


logger=logging.getLogger(__name__)

# COLOR_OK = '\033[92m'
# COLOR_WARNING = '\033[93m'
# COLOR_FAIL = '\033[91m'
# COLOR_END = '\033[0m'

#*************************************************
#
#*************************************************
class Cloudformation(o7lib.aws.base.Base):
    """Class for Cloudformation Stacks for a Profile & Region"""
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#cloudformation

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None):
        super().__init__(profile=profile, region=region)
        self.cfn = self.session.client(
            'cloudformation',
            config=botocore.config.Config(connect_timeout = 5)
        )

        self.s3ForUpload = None



    #*************************************************
    #
    #*************************************************
    def LoadStacks(self, stackName = None):
        """Returns all Stacks for this Session"""

        logger.info('LoadStacks')

        stacks = []
        param={}
        if stackName is not None:
            param['StackName'] = stackName

        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stacks
            resp = self.cfn.describe_stacks(**param)
            #pprint.pprint(resp)

            if 'NextPageToken' in resp:
                param['NextPageToken'] = resp['NextPageToken']
            else:
                done = True

            logger.info(f'LoadStacks: Number of Stacks found {len(resp["Stacks"])}')
            for stack in resp['Stacks'] :

                driftStatus = stack['DriftInformation'].get('StackDriftStatus', '')
                driftDate = stack['DriftInformation'].get('LastCheckTimestamp', None)
                if driftDate is not None:
                    driftStatus = f'{driftStatus} ({driftDate:%Y-%m-%d})'

                stack['DriftStatus'] = driftStatus


                stacks.append(stack)

        return stacks


    #*************************************************
    #
    #*************************************************
    def LoadEvents(self, stackName = None):
        """Returns latest events for a stacks"""
        logger.info('LoadEvents')

        events = []
        param={}
        if stackName is not None:
            param['StackName'] = stackName

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.describe_stack_events
        resp = self.cfn.describe_stack_events(**param)
        #pprint.pprint(resp)


        logger.info(f'LoadEvents: Number of Events found {len(resp["StackEvents"])}')
        for event in resp['StackEvents'] :
            events.append(event)

        return events

    #*************************************************
    #
    #*************************************************
    def LoadResources(self, stackName):
        """Returns all resources for a stack"""

        logger.info('LoadResources')

        ret = []
        param={}
        param['StackName'] = stackName

        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_stack_resources
            resp = self.cfn.list_stack_resources(**param)
            #pprint.pprint(resp)

            if 'NextPageToken' in resp:
                param['NextPageToken'] = resp['NextPageToken']
            else:
                done = True

            logger.info(f'LoadResources: Number of Resource found {len(resp["StackResourceSummaries"])}')
            for rsrc in resp['StackResourceSummaries'] :

                driftStatus = rsrc['DriftInformation'].get('StackResourceDriftStatus', '')
                rsrc['DriftStatus'] = driftStatus
                ret.append(rsrc)

        return ret


    #*************************************************
    #
    #*************************************************
    def LoadDrifters(self, stackName):
        """Return all drifters post a drift detection"""

        logger.info('LoadDrifters for Stack : {stackName}')

        ret = []
        param={'StackName': stackName, 'StackResourceDriftStatusFilters' : ['MODIFIED']}

        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.list_stack_resources
            resp = self.cfn.describe_stack_resource_drifts(**param)
            #pprint.pprint(resp)

            if 'NextPageToken' in resp:
                param['NextPageToken'] = resp['NextPageToken']
            else:
                done = True

            logger.info(f'LoadDrifters: Number of Resource found {len(resp["StackResourceDrifts"])}')

            for rsrc in resp['StackResourceDrifts'] :
                ret.append(rsrc)

        return ret

    #*************************************************
    #
    #*************************************************
    def InitDriftDetection(self, stackName):
        """Initialize the drift verification for a stack"""

        logger.info('InitDriftDetection for stack : {stackName}')

        if o7lib.util.input.IsItOk(f'Confirm Drift Detection for Stack: {stackName}') is False :
            return

        param = {'StackName' : stackName}
        resp = self.cfn.detect_stack_drift(**param)
        pprint.pprint(resp)

        logger.info('InitDriftDetection Response : {resp}')

    #*************************************************
    #
    #*************************************************
    def FindS3ForUpload(self):
        """Find bucket where to upload template file"""
        logger.info(f'FindS3ForUpload')

        buckets = o7lib.aws.s3.S3().LoadBuckets()
        for bucket in buckets:
            if bucket['Region'] == self.session.region_name:
                nameArr = bucket['Name'].split('-')
                if len(nameArr) >= 3:
                    if nameArr[0] == 'cf' and nameArr[1] == 'templates' :
                        logger.info(f'FindS3ForUpload: found bucket {bucket["Name"]}')
                        self.s3ForUpload = bucket['Name']

    #*************************************************
    #
    #*************************************************
    def UploadTemplate(self, filePath):
        """Unload the CFN template to S3 for update or creation"""

        logger.info(f'UploadTemplate: {filePath=}')

        if self.s3ForUpload is None:
            self.FindS3ForUpload()

        if self.s3ForUpload is None:
            logger.error('Not able to find upload bucket')
            return None

        basename = os.path.basename(filePath)
        prefix = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        key = f'{prefix}-{basename}'

        s3Path = o7lib.aws.s3.S3().UploadFile(bucket=self.s3ForUpload, key=key, filePath=filePath)

        logger.info(f'UploadTemplate: Done {s3Path=}')
        return s3Path


    #*************************************************
    #
    #*************************************************
    def ValidateTemplate(self, filePath, stack):
        """Validate and Load a CFN template, returns parameters for Update function"""

        logger.info(f'ValidateTemplate: {filePath=}')



        if filePath is not None :
            # Load File to S3
            s3Path = self.UploadTemplate(filePath)
            try:
                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.validate_template
                response = self.cfn.validate_template(TemplateURL=s3Path)
            except botocore.exceptions.ClientError as error:
                print(f'ValidateTemplate: {error}')
                return None
        else:
            response = stack

        # print('-' * 50)
        # pprint.pprint(stack)
        # print('-' * 50)
        # pprint.pprint(response)
        print('=' * 50)
        print('Stack Update Validation')
        print('=' * 50)
        o7d.PrintParamOk('Name', stack["StackName"])
        print('')

        #---------------------------------
        #  Validate Description
        #---------------------------------
        newDesc = response["Description"].replace('\n', ' ').strip()
        curDesc = stack["Description"].replace('\n', ' ').strip()
        if newDesc == curDesc:
            o7d.PrintParamOk('Description', curDesc)
        else :
            print(f'Current Description -> {o7d.Colors.ERROR}{curDesc}{o7d.Colors.ENDC}')
            print(f'New Description     -> {o7d.Colors.ERROR}{newDesc}{o7d.Colors.ENDC}')
            if o7lib.util.input.IsItOk('Do you Accept a New Description ?') is False:
                return None


        #---------------------------------
        #  Validate Parameters
        #---------------------------------
        tempParameters = []
        for newParam in response.get('Parameters',[]):

            tempsParam = {
                'key' : newParam['ParameterKey'],
                'currentValue' : newParam.get('DefaultValue',""),
                'default' : newParam.get('DefaultValue',""),
                'description' : newParam.get('Description',""),
                'action': 'add'
            }
            # look if current param is there
            for curParam in stack.get('Parameters',[]):
                if curParam['ParameterKey'] == newParam['ParameterKey']:
                    tempsParam['currentValue'] = curParam['ParameterValue']
                    tempsParam['action'] = 'same'
                    break

            tempParameters.append(tempsParam)

        #---------------------------------
        # Look for missing parameters
        #---------------------------------
        for curParam in stack.get('Parameters',[]):
            missing = True
            for tempParam in tempParameters:
                if tempParam['key'] == curParam['ParameterKey']:
                    missing = False

            if missing:
                tempParameters.append({
                    'key' : curParam['ParameterKey'],
                    'currentValue' : curParam['ParameterValue'],
                    'action' : 'delete'
                })

        #---------------------------------
        #  Menu to edit param
        #---------------------------------
        print('')
        params = {
            'columns' : [
                {'title' : 'id'         , 'type': 'i',       'minWidth' : 4  },
                {'title' : 'Name'       , 'type': 'str',  'dataName': 'key'},
                {'title' : 'Action'       , 'type': 'str',  'dataName': 'action', 'format': 'aws-edit'},
                {'title' : 'Current'    , 'type': 'str',  'dataName': 'currentValue'},
                {'title' : 'Description', 'type': 'str',  'dataName': 'description'}
            ]
        }
        tempParameters = sorted(tempParameters, key=lambda x: x['key'])

        while True:
            o7lib.util.table.Table(params, tempParameters).Print()
            keyType, key = o7lib.util.input.InputMulti('Are Those Parameters Acceptable (y/n) Edit Parameter(int):')

            if keyType == 'str':
                if key.lower() == 'y':
                    break
                if key.lower() == 'n':
                    return None

            if keyType == 'int' and key > 0 and key <= len(tempParameters):
                pKey = tempParameters[key-1]["key"]
                pValue = o7lib.util.input.InputString(f'Enter new value for {pKey} -> ')
                tempParameters[key-1]["currentValue"] = pValue
                tempParameters[key-1]['action'] = 'modify'

        #---------------------------------
        #  Validate Capabilies
        #---------------------------------
        capabilities = response.get('Capabilities',[])
        capReason = response.get("CapabilitiesReason","").replace("\n", "").strip()

        if len(capabilities) > 0:
            print('')
            print(f'Required Capabilities : {capabilities}')
            print(f'Reason: {capReason}')
            if o7lib.util.input.IsItOk('Do you Accept Required Capabilities ?') is False:
                return None

        #---------------------------------
        #  Prepare Update stack Parameters
        #---------------------------------
        ret = {
            'StackName' : stack["StackName"],
            'Parameters' : [],
            'Capabilities' : capabilities
        }

        if filePath is not None :
            ret['TemplateURL'] = s3Path
        else:
            ret['UsePreviousTemplate'] = True


        #Building Parameter structure without the deleted parameters
        for parameter in tempParameters:
            if  parameter['action'] != 'delete':
                update = {'ParameterKey' : parameter['key'], 'ParameterValue' : parameter['currentValue'],}
                ret['Parameters'].append(update)

        return ret

    #*************************************************
    #
    #*************************************************
    def UpdateTemplate(self, stackName, filePath):
        """Update the stack template"""

        logger.info(f'UpdateTemplate: {stackName=} {filePath=}')

        stacks = self.LoadStacks(stackName=stackName)
        if len(stacks) == 0:
            logger.error(f'UpdateTemplate: Stack: {stackName} was not found')
            return None
        stack = stacks[0]

        # Validating Template
        updateParam = self.ValidateTemplate(filePath=filePath, stack=stack)
        if updateParam is None:
            logger.error(f'UpdateTemplate: Template Valiadation Failed {filePath=}')
            return None

        logger.debug(f'UpdateTemplate: Ready to Update {updateParam=}')
        #pprint.pprint(updateParam)

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.update_stack
        try:
            respUpdate = self.cfn.update_stack(**updateParam)
        except botocore.exceptions.ClientError as error:
            print(f'Error: {error}')
            return None

        print(f'Success = {respUpdate}')

        return respUpdate


    #*************************************************
    #
    #*************************************************
    def DisplayStacks(self, stacks):
        """Displays a summary of Stacks in a Table Format"""

        self.ConsoleTitle(left='Cloudformation Stacks')
        print('')

        params = {
            'columns' : [
                {'title' : 'id'      , 'type': 'i',       'minWidth' : 4  },
                {'title' : 'Name'    , 'type': 'str',  'dataName': 'StackName'},
                {'title' : 'Creation', 'type': 'date', 'dataName': 'CreationTime'},
                {'title' : 'Updated' , 'type': 'since',  'dataName': 'LastUpdatedTime'},
                {'title' : 'Status'  , 'type': 'str',  'dataName': 'StackStatus', 'format' : 'aws-status'},
                {'title' : 'Reason'  , 'type': 'str',  'dataName': 'StackStatusReason', 'maxWidth' : 50},
                {'title' : 'Drift'     , 'type': 'str',     'width' : 20, 'dataName': 'DriftStatus', 'format' : 'aws-drift'},
            ]
        }
        o7lib.util.table.Table(params, stacks).Print()

    #*************************************************
    #
    #*************************************************
    def DisplayEvents(self, events, maxEvent = None):
        """Displays a summary of Events in a Table Format"""

        self.ConsoleTitle(left='Cloudformation Events in Stack: TBD')
        print('')

        params = {
            'columns' : [
                {'title' : 'id'  , 'type': 'i', 'minWidth' : 4},
                {'title' : 'Date Time'  , 'type': 'datetime','dataName': 'Timestamp'},
                {'title' : 'Logical ID' , 'type': 'str',     'dataName': 'LogicalResourceId'},
                #{'title' : 'Physical ID' , 'type': 'str',     'width' : 30, 'dataName': 'PhysicalResourceId'},
                {'title' : 'Type'       , 'type': 'str',     'dataName': 'ResourceType'},
                {'title' : 'Status'     , 'type': 'str',     'dataName': 'ResourceStatus', 'format' : 'aws-status', 'maxWidth' : 20},
                {'title' : 'Reason'     , 'type': 'str',     'dataName': 'ResourceStatusReason'}
            ]
        }

        if max is not None:
            events = events[0:maxEvent]

        o7lib.util.table.Table(params, events).Print()

        return

    #*************************************************
    #
    #*************************************************
    def DisplayResources(self, resources):
        """Displays a summary of Resources in a Table Format"""

        self.ConsoleTitle(left='Cloudformation Resources for Stack: TBD')
        print('')


        params = {
            'columns' : [
                {'title' : 'Logical ID' , 'type': 'str',     'dataName': 'LogicalResourceId','sort' : 'asc'},
                {'title' : 'Type' , 'type': 'str',     'dataName': 'ResourceType'},
                {'title' : 'Physical ID' , 'type': 'str',    'dataName': 'PhysicalResourceId', 'maxWidth' : 40},
                {'title' : 'Updated'     , 'type': 'datetime','dataName': 'LastUpdatedTimestamp'},
                {'title' : 'Status'     , 'type': 'str',     'dataName': 'ResourceStatus', 'format' : 'aws-status'},
                {'title' : 'Drift'     , 'type': 'str',     'dataName': 'DriftStatus', 'format' : 'aws-drift'},
                {'title' : 'Reason'     , 'type': 'str',     'dataName': 'ResourceStatusReason'},
            ]
        }

        o7lib.util.table.Table(params, resources).Print()

    #*************************************************
    #
    #*************************************************
    def _DisplayDrifters(self, drifters):
        """Displays a summary of Drifters in a Table Format"""

        drifts = []

        for drifter in drifters:
            lId = drifter['LogicalResourceId']
            for diff in drifter['PropertyDifferences']:
                drift = {
                    'LogicalResourceId' : lId,
                    'DifferenceType' : diff['DifferenceType'],
                    'PropertyPath' : diff['PropertyPath'],
                    'ExpectedValue' : diff['ExpectedValue'],
                    'ActualValue' : diff['ActualValue'],
                }
                drifts.append(drift)

        params = {
            'title' : f"List of Drifts - {self.TitleLine()}",
            'columns' : [
                {'title' : 'Logical ID' , 'type': 'str',     'dataName': 'LogicalResourceId', 'sort' : 'asc'},
                {'title' : 'Type' , 'type': 'str',    'dataName': 'DifferenceType'},
                {'title' : 'Property' , 'type': 'str',    'dataName': 'PropertyPath'},
                {'title' : 'Expected' , 'type': 'str',    'dataName': 'ExpectedValue'},
                {'title' : 'Actual' , 'type': 'str',    'dataName': 'ActualValue'}
            ]
        }

        o7lib.util.table.Table(params, drifts).Print()

    #*************************************************
    #
    #*************************************************
    def _DisplayParameters(self, parameters, maxParameters = None):
        """Displays a summary of Parameters in a Table Format"""
        params = {
            'columns' : [
                {'title' : 'id'      , 'type': 'i',       'minWidth' : 4  },
                {'title' : 'Key'            , 'type': 'str',     'width' : 30, 'dataName': 'ParameterKey', 'sort' : 'asc'},
                {'title' : 'Value'          , 'type': 'str',     'width' : 50, 'dataName': 'ParameterValue'},
                {'title' : 'Resolved Value' , 'type': 'str',     'width' : 30, 'dataName': 'ResolvedValue'}
            ]
        }

        if max is not None:
            parameters = parameters[0:maxParameters]


        o7lib.util.table.Table(params, parameters).Print()

    #*************************************************
    #
    #*************************************************
    def DisplayOutputs(self, outputs, maxOutput = None):
        """Displays a summary of Outputs in a Table Format"""


        params = {
            'columns' : [
                {'title' : 'Key'            , 'type': 'str',     'width' : 30, 'dataName': 'OutputKey', 'sort' : 'asc'},
                {'title' : 'Value'          , 'type': 'str',     'width' : 80, 'dataName': 'OutputValue'},
                {'title' : 'Description'    , 'type': 'str',     'width' : 20, 'dataName': 'Description'},
                {'title' : 'Export Name'    , 'type': 'str',     'width' : 30, 'dataName': 'ExportName'}
            ]
        }

        if max is not None:
            outputs = outputs[0:maxOutput]
        o7lib.util.table.Table(params, outputs).Print()

    #*************************************************
    #
    #*************************************************
    def DisplaySingleStack(self, stack):
        """Display details for a specific Stack"""

        self.ConsoleTitle(left=f'Cloudformation Details for Stack: {stack.get("StackName", "")}')
        print('')

        print(f'Description: {stack.get("Description", "")}')
        print(f'Creation: {stack.get("CreationTime", ""):%Y-%m-%d}')
        print(f'Last Updated: {stack.get("LastUpdatedTime", "NA")}')
        print(f'Status: {o7t.FormatAWSStatus(stack.get("StackStatus", ""))}')
        print(f'Status Reason: {stack.get("StackStatusReason", "-")}')

        print(f'Drift Detection: {o7t.FormatAWSDrift(stack.get("DriftStatus", "-"))}')

        print(f'Capabilities: {stack.get("Capabilities", [])}')
        print(f'Tags: {stack.get("Tags", [])}')


        print('')
        print('Parameters')
        self._DisplayParameters(stack.get("Parameters", []))
        print('')
        print('Outputs')
        self.DisplayOutputs(stack.get("Outputs", []))
        print('')

        return

    #*************************************************
    #
    #*************************************************
    def MenuStacks(self):
        """Menu to view and edit all stacks in current region"""

        while True :

            stacks = self.LoadStacks()
            stacks = sorted(stacks, key=lambda x: x['StackName'])
            self.DisplayStacks(stacks)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Details(int): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'r':
                    pprint.pprint(stacks)
                    o7lib.util.input.WaitInput()

            if keyType == 'int' and key > 0 and key <= len(stacks):
                print(f"Printing detailled for stack id: {key}")
                self.MenuSignleStack(stacks[key - 1]['StackName'])





    #*************************************************
    #
    #*************************************************
    def MenuSignleStack(self, stackName):
        """Menu to view and edit a specific stack"""

        while True :

            stacks = self.LoadStacks(stackName)
            stack = stacks[0]
            self.DisplaySingleStack(stack)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Events(e) Resources(s) Init Drift Detection(d) Edit Parameters (p) Update Template (u) : ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'e':
                    self. MenuEvents(stackName)
                if key.lower() == 's':
                    self. MenuResources(stackName)
                if key.lower() == 'r':
                    pprint.pprint(stack)
                    o7lib.util.input.WaitInput()

                if key.lower() == 'p':
                    self.UpdateTemplate(stackName=stackName, filePath=None)
                    o7lib.util.input.WaitInput()

                if key.lower() == 'u':

                    filePath = o7lib.util.file_explorer.FileExplorer().SelectFile(filters={'extensions' : ['.yaml', 'yml'] })
                    if filePath is None:
                        print('No file selected')
                        continue
                    self.UpdateTemplate(stackName=stackName, filePath=filePath)
                    o7lib.util.input.WaitInput()

                if key.lower() == 'd':
                    self.InitDriftDetection(stackName)


    #*************************************************
    #
    #*************************************************
    def MenuEvents(self, stackName):
        """Menu to view and edit a stack events for a stack"""

        maxEvents = 50
        while True :

            maxEvents = o7t.GetHeight() - 7

            events = self.LoadEvents(stackName)
            self.DisplayEvents(events, maxEvents)

            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) All(a) Details(int): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'a':
                    maxEvents = None

            if keyType == 'int' and  0 < key <= len(events):
                print(f"Printing detailled for event id: {key}")
                pprint.pprint(events[key - 1], width=100)
                o7lib.util.input.WaitInput()

    #*************************************************
    #
    #*************************************************
    def MenuResources(self, stackName):
        """Menu to view and edit stack resources fro a stack"""

        while True :

            resources = self.LoadResources(stackName)
            self.DisplayResources(resources)

            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Show Drifters Details(d): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'r':
                    pprint.pprint(resources)
                    o7lib.util.input.WaitInput()
                if key.lower() == 'd':
                    self.MenuDrifters(stackName)


    #*************************************************
    #
    #*************************************************
    def MenuDrifters(self, stackName):
        """Menu to view and edit stack latest drifters"""

        while True :

            drifters = self.LoadDrifters(stackName)
            self._DisplayDrifters(drifters)

            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) : ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'r':
                    pprint.pprint(drifters)

#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    #Cloudformation().MenuStacks()

    Cloudformation().UploadTemplate('/gitcw/red-infra/pipeline-client-test/client-pipeline.yaml')
