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
import datetime

import o7lib.util.input
import o7lib.util.displays
import o7lib.aws.base



logger=logging.getLogger(__name__)

# https://i.stack.imgur.com/6otvY.png
COLOR_HEADER = '\033[5;30;47m'
COLOR_LINE_NUMBER = '\033[0;30;46m'
COLOR_TIMESTAMP = '\033[0;36;40m'
COLOR_END = '\033[0m'



#*************************************************
#
#*************************************************
class Logstream(o7lib.aws.base.Base):
    """Class to access a Cloudwatch Logstream"""
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html

    #*************************************************
    #
    #*************************************************
    def __init__(self, logGroupName, logStreamName, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session=session)
        self.cwlClient = self.session.client('logs')

        self.logGroupName = logGroupName
        self.logStreamName = logStreamName

        self.events = []
        self.maxPerLoad = 2500
        self.fromHead = True
        self.current = 0
        self.nextToken = None
        self.prevToken = None
        self.isLast = False

        self.displayTimestamp = False
        self.displayLineNumber = True



    #*************************************************
    #
    #*************************************************
    def LoadLogsEvents(self):
        """Returns Log Events for Stream"""

        logger.info('LoadLogsEvents')

        param={
            'logGroupName' : self.logGroupName,
            'logStreamName' : self.logStreamName,
            'startFromHead' : self.fromHead
        }

        if self.maxPerLoad is not None:
            param['limit'] = self.maxPerLoad

        done=False
        count=0
        while not done:

            if self.fromHead and self.nextToken is not None:
                param['nextToken'] = self.nextToken
            if not self.fromHead and self.prevToken is not None:
                param['nextToken'] = self.prevToken


            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_log_events
            response = self.cwlClient.get_log_events(**param)
            #pprint.pprint(response)

            if 'nextForwardToken' in response:
                self.nextToken = response['nextForwardToken']

            if 'nextBackwardToken' in response:
                self.prevToken = response['nextBackwardToken']

            # check if max per request is reach
            count += len(response["events"])
            if self.maxPerLoad is not None and count >= self.maxPerLoad:
                done = True

            # check if no more events are available
            if len(response["events"]) == 0:
                done = True

            logger.info(f'LoadLogsEvents: Number of events found {len(response["events"])}')
            if self.fromHead:
                self.events += response["events"]
            else:
                self.events = response["events"] + self.events




    #*************************************************
    # {'ingestionTime': 1632528987638,
    # 'message': '[Container] 2021/09/25 00:16:25 Entering phase POST_BUILD\n',
    # 'timestamp': 1632528987635},
    # {'ingestionTime': 1632528987638,
    # 'message': '[Container] 2021/09/25 00:16:25 Running command echo Test '
    #             'completed on `date`\n',
    # 'timestamp': 1632528987635},
    # {'ingestionTime': 1632528987638,
    # 'message': 'Test completed on Sat Sep 25 00:16:25 UTC 2021\n',
    # 'timestamp': 1632528987635},
    #*************************************************
    def DislayEvents(self):
        """Convert Logs Event to Text"""

        numberWidth = len(str(len(self.events)))

        print(f'{COLOR_HEADER} Log Group: {self.logGroupName} --->> Log Stream: {self.logStreamName} {COLOR_END}')


        for i, event in enumerate(self.events):
            txt = ""

            if self.displayLineNumber:
                txt += f'{COLOR_LINE_NUMBER} {str(i + 1).ljust(numberWidth, " ")} {COLOR_END} '

            if self.displayTimestamp:
                timeStamp = datetime.datetime.fromtimestamp(event.get('timestamp',0) / 1000.0)
                txt += f'{COLOR_TIMESTAMP}[{timeStamp:%Y-%m-%d %H:%M:%S}]{COLOR_END} '

            txt += event.get('message','').strip()
            print(txt)


    #*************************************************
    #
    #*************************************************
    def LogStreamInformation(self):
        """Display informatio  about the Logs Event"""

        direction = ""
        if self.fromHead is True:
            direction = f'First to {len(self.events)}'
        else:
            direction = f'{len(self.events)} to Last'

        return f'{COLOR_HEADER}{direction} | Max per Load: {self.maxPerLoad}{COLOR_END}'



    #*************************************************
    #
    #*************************************************
    def Menu(self, firstLoad = True):
        """Menu to view Log Stream"""

        if firstLoad:
            self.LoadLogsEvents()

        while True :

            self.DislayEvents()

            print(self.LogStreamInformation())
            keyType, key = o7lib.util.input.InputMulti('Options -> Back(b) Raw(r) Load More(l) Timestamp(t) Numbers(n) Max(m): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'l':
                    self.LoadLogsEvents()
                if key.lower() == 't':
                    self.displayTimestamp = not self.displayTimestamp
                if key.lower() == 'n':
                    self.displayLineNumber = not self.displayLineNumber
                if key.lower() == 'm':
                    self.maxPerLoad = o7lib.util.input.InputInt('Maximum Events per Load:')
                if key.lower() == 'r':
                    pprint.pprint(self.events)
                    o7lib.util.input.WaitInput()


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )
