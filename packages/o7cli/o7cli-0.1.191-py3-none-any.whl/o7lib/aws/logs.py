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
"""Module allows to view and access Cloudwatch Logs"""

#--------------------------------
#
#--------------------------------
import logging
import pprint

import o7lib.util.input
import o7lib.util.table
import o7lib.aws.base
import o7lib.aws.logstream


logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class Logs(o7lib.aws.base.Base):
    """Class for Cloudwatch Logs for a Profile & Region"""
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session=session)
        self.cwlClient = self.session.client('logs')


    #*************************************************
    #
    #*************************************************
    def LoadLogGroups(self):
        """Returns all Logs for this Session"""

        logger.info('LoadLogGroups')

        logGroups = []
        param={}


        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_log_groups
            resp = self.cwlClient.describe_log_groups(**param)
            #pprint.pprint(resp)

            if 'nextToken' in resp:
                param['nextToken'] = resp['nextToken']
            else:
                done = True

            logger.info(f'LoadLogs: Number of Log Groups found {len(resp["logGroups"])}')
            for logGroup in resp['logGroups'] :

                logGroups.append(logGroup)

        return logGroups

    #*************************************************
    #
    #*************************************************
    def LoadLogStream(self, groupName, maxStream = None):
        """Returns all Logs Stream for this Group"""

        logger.info('LoadLogStream')

        logStreams = []
        param={
            'logGroupName' : groupName,
            'orderBy' : 'LastEventTime',
            'descending' : True
        }

        if maxStream is not None:
            param['limit'] = maxStream


        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_log_streams
            try:
                resp = self.cwlClient.describe_log_streams(**param)
            except self.cwlClient.exceptions.ResourceNotFoundException as error:
                logger.error(f'Log Group {groupName} does not exist, error: {error}')
                return None
            #pprint.pprint(resp)

            if 'nextToken' in resp:
                param['nextToken'] = resp['nextToken']
            else:
                done = True

            logger.info(f'LoadLogStream: Number of Log Streams found {len(resp["logStreams"])}')
            for logStream in resp['logStreams'] :
                logStreams.append(logStream)

            if maxStream is not None and len(logStreams) >= maxStream:
                done = True

        return logStreams

    #*************************************************
    #
    #*************************************************
    def DisplayLogGroups(self, logGroups):
        """Displays a summary of Log Groups in a Table Format"""

        # Title
        self.ConsoleTitle(left = "Log Groups List")
        print('')

        params = {
            'columns' : [
                {'title' : 'id'      , 'type': 'i',  },
                {'title' : 'Name'    , 'type': 'str',  'dataName': 'logGroupName'},
                {'title' : 'Retention' , 'type': 'str', 'dataName': 'retentionInDays'},
                {'title' : 'Stored Bytes', 'type': 'bytes', 'dataName': 'storedBytes'},
                {'title' : 'Created', 'type': 'datetime', 'dataName': 'creationTime'}
            ]
        }
        o7lib.util.table.Table(params, logGroups).Print()

    #*************************************************
    #
    #*************************************************
    def DisplayLogStreams(self, logStreams):
        """Displays a summary of Log Streams in a Table Format"""

        # Title
        self.ConsoleTitle(left = "Log Streams List for group: tbd")
        print('')

        params = {
            # 'title' : f"Pipelines List - {self.TitleLine()}",
            'columns' : [
                {'title' : 'id'      , 'type': 'i',       'minWidth' : 4  },
                {'title' : 'Name'    , 'type': 'str',  'dataName': 'logStreamName'},
                {'title' : 'First Event' , 'type': 'datetime',  'dataName': 'firstEventTimestamp'},
                {'title' : 'Last Event' , 'type': 'since',  'dataName': 'lastIngestionTime'},
                {'title' : 'Stored Bytes', 'type': 'bytes', 'dataName': 'storedBytes'}
            ]
        }
        o7lib.util.table.Table(params, logStreams).Print()
    #*************************************************
    #
    #*************************************************
    def MenuLogStreams(self, groupName):
        """Menu to list available log stream for a group"""

        while True :

            logStreams = self.LoadLogStream(groupName=groupName, maxStream=25)
            self.DisplayLogStreams(logStreams)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Details(int): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break

                if key.lower() == 'r':
                    pprint.pprint(logStreams)
                    o7lib.util.input.WaitInput()

            if keyType == 'int' and key > 0 and key <= len(logStreams):
                logStream = o7lib.aws.logstream.Logstream(
                    logGroupName=groupName,
                    logStreamName=logStreams[key-1]['logStreamName'],
                    session=self.session
                )
                logStream.Menu()

    #*************************************************
    #
    #*************************************************
    def MenuLogGroups(self):
        """Menu to list available logs"""

        while True :

            logGroups = self.LoadLogGroups()
            self.DisplayLogGroups(logGroups)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Details(int): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break

                if key.lower() == 'r':
                    pprint.pprint(logGroups)
                    o7lib.util.input.WaitInput()

            if keyType == 'int' and key > 0 and key <= len(logGroups):
                self.MenuLogStreams(logGroups[key - 1]['logGroupName'])


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )
