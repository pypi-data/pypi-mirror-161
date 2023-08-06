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
"""Module allows to view and access Codebuild"""

#--------------------------------
#
#--------------------------------
import logging
import pprint

import o7lib.util.input
import o7lib.util.format
import o7lib.util.terminal as o7t
import o7lib.util.table
import o7lib.aws.base
import o7lib.aws.logstream
import o7lib.aws.s3

logger=logging.getLogger(__name__)

COLOR_HEADER = '\033[5;30;47m'
COLOR_END = '\033[0m'

#*************************************************
#
#*************************************************
class CodeBuild(o7lib.aws.base.Base):
    """Class for Codebuil for a Profile & Region"""
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#cloudformation

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session=session)
        self.cbClient = self.session.client('codebuild')



    #*************************************************
    #
    #*************************************************
    def LoadProjects(self, pName = None):
        """Returns all LoadCodeBuilds for this Session"""

        logger.info(f'LoadCodeBuilds {pName=}')

        projects = []
        param={}


        done=False
        while not done:

            paramGet={}

            if pName is None:
                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codebuild.html#CodeBuild.Client.list_builds
                resp = self.cbClient.list_projects(**param)
                #pprint.pprint(resp)

                if 'nextToken' in resp:
                    param['nextToken'] = resp['nextToken']
                else:
                    done = True

                logger.info(f'LoadCodeBuilds: Number of Project found {len(resp["projects"])}')
                if len(resp["projects"]) == 0:
                    return projects

                paramGet['names'] = resp["projects"]

            else:
                done = True
                logger.info(f'LoadCodeBuilds: Getting only project  {pName}')
                paramGet['names'] = [pName]

            respDetails = self.cbClient.batch_get_projects(**paramGet)
            # pprint.pprint(respDetails)
            projects += respDetails["projects"]

        return projects

    #*************************************************
    #
    #*************************************************
    def LoadPastBuilds(self, pName = None, maxBuilds = 25):
        """Returns Details for Past Builds"""

        logger.info(f'LoadPastBuilds {pName=} {maxBuilds=}')

        builds = []
        param={
            'projectName' : pName,
            'sortOrder' : 'DESCENDING'
        }

        done=False
        left=maxBuilds
        while not done:

            paramGet={}

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codebuild.html#CodeBuild.Client.list_builds
            resp = self.cbClient.list_builds_for_project(**param)
            #pprint.pprint(resp)

            if 'nextToken' in resp:
                param['nextToken'] = resp['nextToken']
            else:
                done = True

            if len(resp["ids"]) >= left:
                done = True

            logger.info(f'LoadPastBuilds: Number of Build found {len(resp["ids"])}')
            if len(resp["ids"]) == 0:
                return builds

            paramGet['ids'] = resp["ids"][:left]


            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codebuild.html#CodeBuild.Client.batch_get_builds
            respDetails = self.cbClient.batch_get_builds(**paramGet)
            # pprint.pprint(respDetails)
            builds += respDetails["builds"]


        for build in builds:
            if 'startTime' in build:
                if 'endTime' in build:
                    build['diffTime'] = build['endTime'] - build['startTime']
                else:
                    build['diffTime'] = build['startTime']

        return builds

    #*************************************************
    #
    #*************************************************
    def LoadBuildDetails(self, execId):
        """Returns Execution Details of a Buiild"""

        logger.info(f'LoadBuildDetail {execId=}')

        param={
            'ids': [execId]
        }
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codebuild.html#CodeBuild.Client.batch_get_builds
        response = self.cbClient.batch_get_builds(**param)
        #pprint.pprint(response)

        if 'builds' not in response:
            return None

        if len(response['builds']) < 1:
            return None

        build = response['builds'][0]
        for phase in build.get("phases",[]):
            phase['contextMessage'] = phase.get('contexts',[{}])[0].get('message','')

        if 'endTime' in build:
            build['diffTime'] = build['endTime'] - build['startTime']

        return build

    #*************************************************
    #
    #*************************************************
    def StartBuild(self, pName):
        """Start a New Build"""

        logger.info(f'StartBuilds {pName=}')

        param={
            'projectName': pName
        }
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codebuild.html#CodeBuild.Client.batch_get_builds
        response = self.cbClient.start_build(**param)
        return response


    #*************************************************
    #
    #*************************************************
    def UpdateEnvVariable(self, pName, varName, varValue):
        """Initialize the drift verification for a stack"""

        logger.info(f'UpdateEnvVariable: {pName=} {varName=} {varValue=}')

        projects = self.LoadProjects(pName=pName)
        if len(projects) == 0:
            logger.error(f'UpdateEnvVariable: Project: {pName} was not found')
            return None

        environment = projects[0]['environment']
        found = False
       # Modify Env structure
        for envVar in environment.get('environmentVariables',[]):
            if envVar['name'] == varName:
                envVar['value'] = varValue
                found = True

        if found is False:
            logger.error(f'UpdateEnvVariable: Variable: {varName} was not found')
            return None

        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codebuild.html#CodeBuild.Client.update_project
        param = {
            'name' : pName,
            'environment': environment
        }
        #pprint.pprint(param)
        self.cbClient.update_project(**param)
        #pprint.pprint(resp)



    #*************************************************
    #
    #*************************************************
    def DisplayProjects(self, projects):
        """Displays a summary of Projects in a Table Format"""
        self.ConsoleTitle(left='Codebuild Project List')
        print('')
        params = {
            'columns' : [
                {'title' : 'id'      , 'type': 'i',       'minWidth' : 4  },
                {'title' : 'Name'    , 'type': 'str',  'dataName': 'name'},
                {'title' : 'Creation', 'type': 'date', 'dataName': 'created'},
                {'title' : 'Description' , 'type': 'str', 'dataName': 'description'},
            ]
        }
        o7lib.util.table.Table(params, projects).Print()


    #*************************************************
    #
    #*************************************************
    def DisplayProjectDetails(self, details, builds = None):
        """Displays the details of a project"""

        if builds is None:
            builds = []

        # Title
        self.ConsoleTitle(left = f'Project Details for : {details.get("name", "NA")}')

        # General Information
        print(f'Description: {details.get("description", "NA")}')
        print(f'Created: {details.get("created", None):%Y-%m-%d %H:%M:%S}')
        print(f'Modified: {o7lib.util.format.ElapseTime(details.get("lastModified", None))} ago')
        print(f'Tags: { details.get("tags", "None")}')

        print('')
        env = details.get("environment", {})
        print(f'Type: {env.get("type", "")}')
        print(f'Compute Type: {env.get("computeType", "")}')
        print(f'Image: {env.get("image", "")}')

        # Env Var
        envVarParams = {
            'title' : "Environment Variables",
            'columns' : [
                {'title' : 'id'      , 'type': 'i',       'minWidth' : 4  },
                {'title' : 'Type' , 'type': 'str', 'dataName': 'type'},
                {'title' : 'Name' , 'type': 'str', 'dataName': 'name'},
                {'title' : 'Value' , 'type': 'str', 'dataName': 'value'},
            ]
        }
        o7lib.util.table.Table(envVarParams, env.get("environmentVariables",[])).Print()
        print('')
        print(f'Service Role: {details.get("serviceRole", "")}')
        print('')
        print(f'Last {len(builds)} builds')
        # Env Var
        pastBuildParams = {
            'columns' : [
                {'title' : 'id'      , 'type': 'i',       'minWidth' : 4  },
                {'title' : 'Started' , 'type': 'datetime', 'dataName': 'startTime'},
                {'title' : 'Status' , 'type': 'str', 'dataName': 'buildStatus', 'format' : 'aws-status'},
                {'title' : 'Phase' , 'type': 'str', 'dataName': 'currentPhase'},
                {'title' : 'Duration' , 'type': 'since', 'dataName': 'diffTime'}

            ]
        }
        o7lib.util.table.Table(pastBuildParams, builds).Print()



        print('')


    #*************************************************
    #
    #*************************************************
    def DisplayBuildDetails(self, details):
        """Displays the details of a builds"""

        # Title
        self.ConsoleTitle(left = f'Build Execution id: {details.get("id", "NA")}')

        # General Information
        print(f'Project Name: {details.get("projectName", "NA")}')
        print(f'Start Time: {details.get("startTime", None):%Y-%m-%d %H:%M:%S}')
        print(f'Duration: {o7lib.util.format.ElapseTime(details.get("diffTime", None))}')
        print(f'Status: { o7t.FormatAWSStatus(details.get("buildStatus", "NA"))}')
        print(f'Artifacts: {details.get("artifacts", {}).get("location", "")}')
        print('')
        env = details.get("environment", {})
        print(f'Type: {env.get("type", "")}   Compute: {env.get("computeType", "") }')


        # Env Var
        envVarParams = {
            'title' : "Environment Variables",
            'columns' : [
                {'title' : 'Type' , 'type': 'str', 'dataName': 'type'},
                {'title' : 'Name' , 'type': 'str', 'dataName': 'name'},
                {'title' : 'Value' , 'type': 'str', 'dataName': 'value'},
            ]
        }
        o7lib.util.table.Table(envVarParams, env.get("environmentVariables",[])).Print()

        print('')
        # Phases Status
        phaseParams = {
            'title' : "Build Phases",
            'columns' : [
                {'title' : 'Type'    , 'type': 'str',  'dataName': 'phaseType'},
                {'title' : 'Started', 'type': 'datetime', 'dataName': 'startTime'},
                {'title' : 'Sec.', 'type': 'str', 'dataName': 'durationInSeconds'},
                {'title' : 'Status' , 'type': 'str', 'dataName': 'phaseStatus', 'format' : 'aws-status'},
                {'title' : 'Message', 'type': 'str', 'dataName': 'contextMessage'}
            ]
        }
        o7lib.util.table.Table(phaseParams, details.get("phases",[])).Print()

        print('')
        # Phases Status
        exportParams = {
            'title' : "Exported Environment Variables",
            'columns' : [
                {'title' : 'id'    , 'type': 'i'},
                {'title' : 'Name', 'type': 'str', 'dataName': 'name'},
                {'title' : 'Value', 'type': 'str', 'dataName': 'value'}
            ]
        }
        o7lib.util.table.Table(exportParams, details.get("exportedEnvironmentVariables",[])).Print()



    #*************************************************
    #
    #*************************************************
    def MenuBuildDetail(self, execId):
        """Menu to view details of a build"""

        if execId is None:
            print('No Code Build Execution Id')
            return

        while True :
            details = self.LoadBuildDetails(execId)
            self.DisplayBuildDetails(details)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) View Logsstream(l) View Build Spec (v) View Artifacts (a): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'r':
                    pprint.pprint(details)
                    o7lib.util.input.WaitInput()
                if key.lower() == 'v':
                    print(details.get('source',{}).get('buildspec','NA'))
                    o7lib.util.input.WaitInput()
                if key.lower() == 'l':
                    logs = details.get('logs',{})
                    o7lib.aws.logstream.Logstream(
                        logGroupName=logs.get('groupName',None),
                        logStreamName=logs.get('streamName', None),
                        session=self.session
                    ).Menu()
                if key.lower() == 'a':
                    artiLoc = details.get("artifacts", {}).get("location", "")
                    if artiLoc.startswith('arn:aws:s3:::'):
                        artiLoc = artiLoc[len('arn:aws:s3:::'):]
                        bucket = artiLoc.split('/')[0]
                        folder = artiLoc[len(bucket)+1:]
                        o7lib.aws.s3.S3(session = self.session).MenuFolder(bucket=bucket, folder=folder)
                    else:
                        print('Artifacts is not an S3 bucket')
                        o7lib.util.input.WaitInput()




    #*************************************************
    #
    #*************************************************
    def MenuProjectDetail(self, pName):
        """Menu to view details of a build"""

        while True :
            projects = self.LoadProjects(pName=pName)
            project = {}
            builds = []
            if len(projects) > 0 :
                project = projects[0]
                builds = self.LoadPastBuilds(pName=pName, maxBuilds=20)

            self.DisplayProjectDetails(project, builds)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Start New Build (s) View Build Spec (v) Edit Env Var (e): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break

                if key.lower() == 'r':
                    pprint.pprint(project)
                    o7lib.util.input.WaitInput()

                if key.lower() == 'v':
                    print(project.get('source',{}).get('buildspec','NA'))
                    o7lib.util.input.WaitInput()

                if key.lower() == 'e':

                    eId = o7lib.util.input.InputInt('Enter Env. Variable Id to Edit -> ')
                    envVar = project.get("environment", {}).get("environmentVariables",[])
                    if eId is None or  len(envVar) < eId <= 0 :
                        print('Invalid Env Variable Id')
                        continue

                    eName = envVar[eId-1]["name"]
                    eValue = o7lib.util.input.InputString(f'Enter new value for {eName} -> ')
                    if o7lib.util.input.IsItOk(f'Confirm that {eName} -> {eValue}'):
                        self.UpdateEnvVariable(pName=pName, varName=eName, varValue=eValue)

                    o7lib.util.input.WaitInput()

                if key.lower() == 's':
                    answer = o7lib.util.input.IsItOk('Confirm you want to start a new build')
                    if answer is False:
                        continue
                    newBuilds = self.StartBuild(pName)
                    pprint.pprint(newBuilds)
                    o7lib.util.input.WaitInput()


            if keyType == 'int' and key > 0 and key <= len(builds):
                self.MenuBuildDetail(builds[key - 1].get('id'))



    #*************************************************
    #
    #*************************************************
    def MenuProjects(self):
        """Menu to view and edit all codebuild projects in current region"""

        while True :

            projects = self.LoadProjects()
            self.DisplayProjects(projects)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Details(int): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break


            if keyType == 'int' and key > 0 and key <= len(projects):
                self.MenuProjectDetail(projects[key - 1].get('name'))


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    CodeBuild().MenuProjects()
