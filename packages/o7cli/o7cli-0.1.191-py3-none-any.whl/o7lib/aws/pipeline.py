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
"""Module allows to view and access Pipelines"""

#--------------------------------
#
#--------------------------------
import logging
import pprint

import botocore

import o7lib.util.input
import o7lib.util.table
import o7lib.util.terminal as o7t
import o7lib.aws.base
import o7lib.aws.codebuild


logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class Pipeline(o7lib.aws.base.Base):
    """Class for Pipelines for a Profile & Region"""
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#cloudformation

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session=session)

        self.ppClient = self.session.client(
            'codepipeline',
            config=botocore.config.Config(connect_timeout = 5)
        )



    #*************************************************
    #
    #*************************************************
    def LoadPipelines(self):
        """Returns all Pipelines for this Session"""

        logger.info('LoadPipelines')

        pipelines = []
        param={}


        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codepipeline.html#CodePipeline.Client.list_pipelines
            resp = self.ppClient.list_pipelines(**param)
            #pprint.pprint(resp)

            if 'nextToken' in resp:
                param['nextToken'] = resp['nextToken']
            else:
                done = True

            logger.info(f'LoadPipelines: Number of Pipelines found {len(resp["pipelines"])}')
            for pipeline in resp['pipelines'] :

                # Get status of the last Excution
                lastExec = self.LoadExecutions(pipeline['name'], maxExec=1)
                pipeline['execStart'] = lastExec[0].get('startTime','NA')
                pipeline['execStatus'] = lastExec[0].get('status','NA')

                pipelines.append(pipeline)

        return pipelines


    #*************************************************
    #
    #*************************************************
    def LoadPipelineDetails(self, plName):
        """Returns Details for a Pipeline"""

        logger.info('LoadPipelineDetails')

        param={
            'name' : plName
        }

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codepipeline.html#CodePipeline.Client.get_pipeline
        respPl= self.ppClient.get_pipeline(**param)

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codepipeline.html#CodePipeline.Client.get_pipeline_state
        respState = self.ppClient.get_pipeline_state(**param)
        #pprint.pprint(respState)

        if 'pipeline' not in respPl:
            return None

        if 'stageStates' not in respState:
            return respPl['pipeline']

        actionId = 1

        # Merge Stage & Action State
        for stage in respPl['pipeline']['stages']:

            #print(f'processing stage {stage["name"]}')
            stage['status'] = 'na'

            for stageState in respState['stageStates']:
                if stageState['stageName'] == stage['name'] :

                    # FOUND Stage
                    #print(f'  fOUND stage state->'); pprint.pprint(stageState)

                    #LoadExecutionDetail

                    stage['latestExecution'] = stageState.get('latestExecution',{})
                    stage['status'] = stage['latestExecution'].get('status','')
                    stage['inboundTransitionState'] = stageState.get('inboundTransitionState',{})

                    execId=stage['latestExecution'].get('pipelineExecutionId',None)
                    stage['latestExecutionDetails'] = self.LoadExecutionDetail(plName=plName, execId=execId)

                    for action in  stage['actions']:

                        #print(f'  processing action {action["name"]}')
                        action['status'] = 'na'
                        action['id'] = actionId
                        actionId += 1

                        for actionState in stageState['actionStates']:
                            if actionState['actionName'] == action['name'] :

                                # Found Action
                                action['latestExecution'] = actionState.get('latestExecution',{})
                                action['status'] = action['latestExecution'].get('status','-')
                                action['statusDate'] = action['latestExecution'].get('lastStatusChange', None)
                                action['statusMsg'] = action['latestExecution'].get('errorDetails', {}).get('message','')

        #pprint.pprint(respPl)
        return respPl['pipeline']

    #*************************************************
    #
    #*************************************************
    def LoadExecutionDetails(self, plName, execId):
        """Returns Details for a Pipeline Execution"""

        logger.info(f'LoadExecutionDetails {plName=} {execId=}')

        param={
            'pipelineName' : plName,
            'filter': {'pipelineExecutionId': execId}
        }

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codepipeline.html#CodePipeline.Client.get_pipeline_execution
        respExec= self.ppClient.get_pipeline_execution(pipelineName=plName, pipelineExecutionId=execId)
        #pprint.pprint(respExec)

        if 'pipelineExecution' not in respExec:
            return None

        details = respExec['pipelineExecution']
        details['actions'] = []

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codepipeline.html#CodePipeline.Client.list_action_executions
        respActions= self.ppClient.list_action_executions(**param)
        #pprint.pprint(respActions)


        if 'actionExecutionDetails' not in respActions:
            return details

        actionId = 1

        # # Merge Actions with summary
        for action in reversed(respActions['actionExecutionDetails']):

            logger.info(f'{actionId}. {action["stageName"]=} {action["actionName"]=}')

            action['id'] = actionId
            actionId += 1
            details['actions'].append(action)

        return details

    #*************************************************
    #
    #*************************************************
    def LoadExecutions(self, plName, maxExec = None):
        """Returns Execution Summaries for a Pipeline"""

        logger.info(f'LoadExecutions for {plName}')

        ret = []
        param={'pipelineName' : plName}

        if maxExec is not None:
            param['maxResults'] = maxExec


        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codepipeline.html#CodePipeline.Client.list_pipeline_executions
            resp = self.ppClient.list_pipeline_executions(**param)
            #pprint.pprint(resp)

            if 'nextToken' in resp:
                param['nextToken'] = resp['nextToken']
            else:
                done = True

            logger.info(f'LoadExecutions: Number of Summaries found {len(resp["pipelineExecutionSummaries"])}')
            for execSum in resp['pipelineExecutionSummaries'] :

                execSum['sourceSummary'] = 'No Source'
                sourceRevisions = execSum.get('sourceRevisions',[])
                if len(sourceRevisions) >= 1:
                    execSum['sourceSummary'] = sourceRevisions[0].get('revisionSummary','NA')

                execSum['sourceSummary'] = execSum['sourceSummary'].replace('\n', ' ').strip()
                ret.append(execSum)

            if maxExec is not None and len(ret) >= maxExec:
                done = True

        return ret


    #*************************************************
    #
    #*************************************************
    def SetApprovalResult(self, plName, stageName, actionName, token, approved = False, reason = '' ):
        """Set approval for a pending action"""

        logger.info(f'SetApprovalResult for {plName}')

        param={
            'pipelineName' : plName,
            'stageName' : stageName,
            'actionName' : actionName,
            'result' : {'summary' : reason},
            'token' : token
        }

        if approved:
            param['result']['status'] = 'Approved'
        else:
            param['result']['status'] = 'Rejected'

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codepipeline.html#CodePipeline.Client.put_approval_result
        response = self.ppClient.put_approval_result(**param)

        return response.get('approvedAt', None)

    #*************************************************
    #
    #*************************************************
    def RetryFailStage(self, plName, stageName, execId):
        """Retry Falied Actin in a stage"""

        logger.info(f'SetApprovalResult for {plName}')

        param={
            'pipelineName' : plName,
            'stageName' : stageName,
            'pipelineExecutionId' : execId,
            'retryMode' : 'FAILED_ACTIONS'
        }

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codepipeline.html#CodePipeline.Client.retry_stage_execution
        response = self.ppClient.retry_stage_execution(**param)

        return response.get('pipelineExecutionId', None)


    #*************************************************
    #
    #*************************************************
    def StartExecution(self, plName):
        """Start a new Excution with the latest commit"""

        logger.info(f'StartExecution for {plName}')

        param={
            'name' : plName
        }

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codepipeline.html#CodePipeline.Client.retry_stage_execution
        response = self.ppClient.start_pipeline_execution(**param)

        return response.get('pipelineExecutionId', None)

    #*************************************************
    #
    #*************************************************
    def LoadExecutionDetail(self, plName, execId = None):
        """Returns Execution Details"""

        logger.info(f'LoadExecutionDetail: {plName=} {execId=}')

        if execId is None:
            return {}

        params ={'pipelineName' : plName, 'pipelineExecutionId' : execId}

        try:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codepipeline.html#CodePipeline.Client.get_pipeline_execution
            response = self.ppClient.get_pipeline_execution(**params)
            #pprint.pprint(response)
        except self.ppClient.exceptions.PipelineExecutionNotFoundException:
            return {}

        logger.info(f'LoadExecutionDetail: {response=}')

        if 'pipelineExecution' not in response:
            return {}

        return response['pipelineExecution']

    #*************************************************
    #
    #*************************************************
    def DisplayPipelines(self, pipelines):
        """Displays a summary of Pipelines in a Table Format"""

        # Title
        self.ConsoleTitle(left = "Pipelines List")
        print('')

        params = {
            # 'title' : f"Pipelines List - {self.TitleLine()}",
            'columns' : [
                {'title' : 'id'      , 'type': 'i',       'minWidth' : 4  },
                {'title' : 'Name'    , 'type': 'str',  'dataName': 'name'},
                {'title' : 'Version' , 'type': 'str', 'dataName': 'version'},
                {'title' : 'Creation', 'type': 'date', 'dataName': 'created'},
                {'title' : 'Updated' , 'type': 'since',  'dataName': 'updated'},
                {'title' : 'Last Execution' , 'type': 'since',  'dataName': 'execStart'},
                {'title' : 'Status' ,  'type': 'str',  'dataName': 'execStatus', 'format' : 'aws-status'},
            ]
        }
        o7lib.util.table.Table(params, pipelines).Print()


    #*************************************************
    #
    #*************************************************
    def DisplayPipelineDetails(self, plDetails):
        """Displays a summary of Pipelines in a Table Format"""

        self.ConsoleTitle(left = f'Details for Pipeline : {plDetails.get("name", "-")}')

        print(f'Version: {plDetails.get("version", "NA")}')
        print(f'Role: {plDetails.get("roleArn", "NA")}')

        artifactStore = plDetails.get("artifactStore",{})
        print(f'Artifact Store Type: {artifactStore.get("type", "NA")}  -> Location: {artifactStore.get("location", "NA")}')


        stages = plDetails.get("stages",[])
        stageParams = {
            'columns' : [
                {'dataName': 'id'        , 'title' : 'id'    , 'type': 'int',   'fixWidth' : 4  },
                {'dataName': 'name'      , 'title' : 'Name'  , 'type': 'str'},
                {'dataName': 'runOrder'  , 'title' : 'Order' , 'type': 'int'},
                {'dataName': 'status'    , 'title' : 'Status' , 'type': 'str',   'format': 'aws-status' },
                {'dataName': 'statusDate', 'title' : 'Updated' , 'type': 'since','format': 'aws-status' },
                {'dataName': 'statusMsg' , 'title' : 'Message' , 'type': 'str',  'format': 'aws-status' },
            ]
        }

        for stage in stages:

            # Check if Inbound Allowed
            if 'inboundTransitionState' in stage:
                allowed = stage['inboundTransitionState'].get('enabled', True)
                if allowed:
                    print(" | ")
                else:
                    print(f" X  Disable Reason: {stage['inboundTransitionState'].get('disabledReason', 'NA')}")

            status =o7t.FormatAWSStatus(stage.get('status', '-'))
            execId = stage.get('latestExecution',{}).get('pipelineExecutionId', '-')

            revSummary = []
            for rev in stage.get('latestExecutionDetails',{}).get('artifactRevisions', []):
                revSummary.append(rev.get('revisionSummary','NA').split('\n')[0].strip())
            revSummary = " / ".join(revSummary)

            print(f"Stage: {stage.get('name', '-')}  Execution ID: {execId} ({revSummary})")
            print(f"Status: {status} ")

            o7lib.util.table.Table(stageParams, stage.get('actions',[])).Print()

    #*************************************************
    #
    #*************************************************
    def DisplayExecutions(self, executions):
        """Displays a summary of Pipelines Executions in a Table Format"""

        self.ConsoleTitle(left='Pipelines Executions')
        print('')

        params = {
            'columns' : [
                {'title' : 'id'      , 'type': 'i',       'minWidth' : 4  },
                {'title' : 'Execution Id', 'type': 'str',  'dataName': 'pipelineExecutionId'},
                {'title' : 'Status'      , 'type': 'str',  'dataName': 'status', 'format' : 'aws-status'},
                {'title' : 'Started'     , 'type': 'datetime',  'dataName': 'startTime'},
                {'title' : 'Updated'     , 'type': 'since',  'dataName': 'lastUpdateTime'},
                {'title' : 'Summary'     , 'type': 'str',  'dataName': 'sourceSummary'}
            ]
        }
        o7lib.util.table.Table(params, executions).Print()

    #*************************************************
    #
    #*************************************************
    def DisplayExecutionDetails(self, execDetails):
        """Displays a Details of a pipeline execution"""

        self.ConsoleTitle(left = f'Execution Details for Pipeline : {execDetails.get("pipelineName", "-")}')

        print(f'ExecId : {execDetails.get("pipelineExecutionId", "-")}')

        status = o7t.FormatAWSStatus(execDetails.get('status', '-'))
        print(f'Status: {status} ({execDetails.get("statusSummary", "-")})')
        print(f'Version: {execDetails.get("pipelineVersion", "NA")}')

        print('Artefacts')

        # artefactParams = {
        #     'columns' : [
        #         {'dataName': 'name'                          , 'title' : 'Name'     , 'type': 'str' },
        #         {'dataName': 'revisionSummary.ProviderType'  , 'title' : 'Provider' , 'type': 'str' },
        #         {'dataName': 'revisionSummary.CommitMessage'  , 'title' : 'Commit Message' , 'type': 'str' }
        #     ]
        # }


        # Code Commit
        # 'artifactRevisions': [{'name': 'SourceCode',
        #                         'revisionId': '7996a5624024d8610d73036b75a78110e35405b3',
        #                         'revisionSummary': 'Renamed api/detention.controller\n',
        #                         'revisionUrl': 'https://console.aws.amazon.com/codecommit/home?region=ca-central-1#/repository/dragon-backend/commit/7996a5624024d8610d73036b75a78110e35405b3'}],
        # replace('\n', ' ').strip()

        artefactParams = {
            'columns' : [
                {'dataName': 'name'                          , 'title' : 'Name'     , 'type': 'str' },
                {'dataName': 'revisionSummary'  , 'title' : 'Revision Summary' , 'type': 'str' },
            ]
        }
        o7lib.util.table.Table(artefactParams, execDetails.get("artifactRevisions", [])).Print()

        print('')
        print('Actions')
        actions = execDetails.get("actions",[])

         # Compile for Action variables
        outputVariables = []
        for action in actions:
            action['fullName'] = f"{action.get('stageName', '')}.{action.get('actionName', '')}"

            action['diffTime'] = None
            if 'startTime' in action and 'lastUpdateTime' in action:
                action['diffTime'] = action['lastUpdateTime'] - action['startTime']

            namespace = action.get('input', {}).get('namespace', '')

            actionOutput = action.get('output', {}).get('outputVariables', {})
            for outputKey in actionOutput.keys():
                outputVariables.append({
                    'action' : action["actionName"],
                    'name' : f'{namespace}.{outputKey}',
                    'value' : actionOutput[outputKey]
                })


        actionParams = {
            'columns' : [
                {'dataName': 'id'        , 'title' : 'id'    , 'type': 'int',   'fixWidth' : 4  },
                {'dataName': 'fullName', 'title' : 'Name'  , 'type': 'str' },
                {'dataName': 'status'    , 'title' : 'Status' , 'type': 'str', 'fixWidth' : 10, 'format': 'aws-status' },
                {'dataName': 'startTime', 'title' : 'Started' , 'type': 'datetime' },
                {'dataName': 'diffTime', 'title' : 'Duration' , 'type': 'since' },
                {'dataName': 'lastUpdateTime', 'title' : 'Last Updated' , 'type': 'since'}
            ]
        }
        o7lib.util.table.Table(actionParams, actions).Print()


        print('')
        print('Output Variables')
        outvarParams = {
            'columns' : [
                { 'title' : 'id'    , 'type': 'i',   'fixWidth' : 4  },
                {'dataName': 'action', 'title' : 'Action'  , 'type': 'str' },
                {'dataName': 'name', 'title' : 'Name'  , 'type': 'str' },
                {'dataName': 'value', 'title' : 'Value'  , 'type': 'str' }
            ]
        }
        o7lib.util.table.Table(outvarParams, outputVariables).Print()


        # for stage in stages:

        #     # Check if Inbound Allowed
        #     if 'inboundTransitionState' in stage:
        #         allowed = stage['inboundTransitionState'].get('enabled', True)
        #         if allowed:
        #             print(" | ")
        #         else:
        #             print(f" X  Disable Reason: {stage['inboundTransitionState'].get('disabledReason', 'NA')}")

        #     status = o7lib.util.displays.FormatAWSStatus(stage.get('status', '-'))
        #     execId = stage.get('latestExecution',{}).get('pipelineExecutionId', '-')

        #     revSummary = []
        #     for rev in stage.get('latestExecutionDetails',{}).get('artifactRevisions', []):
        #         revSummary.append(rev.get('revisionSummary','NA').split('\n')[0].strip())
        #     revSummary = " / ".join(revSummary)

        #     print(f"Stage: {stage.get('name', '-')}  Execution ID: {execId} ({revSummary})")
        #     print(f"Status: {status} ")


    #*************************************************
    #
    #*************************************************
    def MenuPipelines(self):
        """Menu to view and edit all pipelines in current region"""

        while True :

            pipelines = self.LoadPipelines()
            self.DisplayPipelines(pipelines)
            keyType, key = o7lib.util.input.InputMulti('Options -> Back(b) Raw(r) Details(int):')

            if keyType == 'str':
                if key.lower() == 'b':
                    break

                if key.lower() == 'r':
                    pprint.pprint(pipelines)
                    o7lib.util.input.WaitInput()

            if keyType == 'int' and key > 0 and key <= len(pipelines):
                self.MenuPipelineDetails(pipelines[key - 1]['name'])


    #*************************************************
    #
    #*************************************************
    def MenuActionDetails(self, plName, stageName, execId, action):
        """Menu to view and act on a Action"""

        print('--- Action Details ---')
        pprint.pprint(action)

        status = action.get('status','')
        actionCat = action.get('actionTypeId',{}).get('category', '')
        actionProvider = action.get('actionTypeId',{}).get('provider', '')

        externalExecutionId = action.get('latestExecution',{}).get('externalExecutionId',None)

        if actionProvider == 'Manual' and status == 'InProgress' and  actionCat == 'Approval' :

            key = o7lib.util.input.InputString('Option -> Approve(a) Reject(r) Back (any other) :')

            if key != 'a' and  key != 'r':
                return

            txt = 'Rejection'
            approved = False
            if key == 'a':
                txt = 'Approval'
                approved = True

            reason = o7lib.util.input.InputString(f'Reason for {txt} :')
            if len(reason) < 1 :
                return

            token  = action.get('latestExecution',{}).get('token', '')
            self.SetApprovalResult(
                plName = plName,
                stageName = stageName,
                actionName= action.get('name',''),
                token=token, approved=approved, reason=reason
            )

        if status == 'Failed':

            if actionProvider == 'CodeBuild' :
                key = o7lib.util.input.InputString('Option -> Retry(r) Details(d) Back (any) :')
            else:
                key = o7lib.util.input.InputString('Option -> Retry(r) Back (any) :')

            if key == 'r':
                self.RetryFailStage(plName=plName, stageName=stageName, execId=execId)
            elif key == 'd':
                o7lib.aws.codebuild.CodeBuild(session = self.session).MenuBuildDetail(externalExecutionId)

        elif actionProvider == 'CodeBuild':
            key = o7lib.util.input.InputString('Option -> Details(d) Back (any) :')
            if key == 'd':
                o7lib.aws.codebuild.CodeBuild(session = self.session).MenuBuildDetail(externalExecutionId)

        else:
            o7lib.util.input.WaitInput()


    #*************************************************
    #
    #*************************************************
    def MenuExecutionDetails(self, plName, execId):
        """Menu to view details of a pipeline execution"""

        while True :
            execDetails = self.LoadExecutionDetails(plName, execId=execId)
            self.DisplayExecutionDetails(execDetails)

            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) : ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break

                if key.lower() == 'r':
                    pprint.pprint(execDetails)
                    o7lib.util.input.WaitInput()

            if keyType == 'int' and key > 0 and key <= len(execDetails['actions']):
                pprint.pprint(execDetails['actions'][key - 1])
                o7lib.util.input.WaitInput()


    #*************************************************
    #
    #*************************************************
    def MenuExecutions(self, plName):
        """Menu to view execution list of a pipeline"""

        while True :
            executions = self.LoadExecutions(plName, maxExec=25)
            self.DisplayExecutions(executions)

            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Execution Details(int) : ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break

                if key.lower() == 'r':
                    pprint.pprint(executions)
                    o7lib.util.input.WaitInput()

            if keyType == 'int' and key > 0 and key <= len(executions):
                #pprint.pprint(executions[key - 1])
                self.MenuExecutionDetails(plName=plName, execId=executions[key - 1]['pipelineExecutionId'])





    #*************************************************
    #
    #*************************************************
    def MenuPipelineDetails(self, plName):
        """Menu to view and edit a specific pipeline"""

        while True :

            plDetails = self.LoadPipelineDetails(plName)
            self.DisplayPipelineDetails(plDetails)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Executions List(e) Re-Start (s)  Action Details(int) : ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'r':
                    pprint.pprint(plDetails)
                    o7lib.util.input.WaitInput()

                if key.lower() == 's':
                    answer = o7lib.util.input.IsItOk('Confirm you want to start a Execution')
                    if answer is False:
                        continue
                    newExec = self.StartExecution(plName=plName)
                    pprint.pprint(newExec)
                    o7lib.util.input.WaitInput()

                if key.lower() == 'e':
                    self.MenuExecutions(plName)

            if keyType == 'int' :
                for stage in plDetails.get("stages",[]):
                    for action in stage.get('actions',[]):
                        if action['id'] == key:
                            execId = stage.get('latestExecution',{}).get('pipelineExecutionId', 'na')
                            self.MenuActionDetails(plName=plName, stageName=stage['name'], execId=execId, action=action)



#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    #Pipeline(region='us-east-1').MenuPipelines()
