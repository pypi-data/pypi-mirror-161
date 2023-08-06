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
"""Module allows to Open Remote Session"""

#--------------------------------
#
#--------------------------------
import logging
import pprint

import o7lib.util.input
import o7lib.util.terminal as o7t
import o7lib.aws.base


logger=logging.getLogger(__name__)



#*************************************************
#
#*************************************************
class SessionManager(o7lib.aws.base.Base):
    """Class for Session Manager"""
    #

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session=session)
        self.ssmClient = self.session.client('ssm')



    #*************************************************
    #
    #*************************************************
    def StartSession(self, instanceId : str):
        """ Open a Terminal Session with a instanece"""

        logger.info(f'OpenSession: Open session with {instanceId}')

        try:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.start_session
            response =  self.ssmClient.start_session(
                Target=instanceId,
                DocumentName='SSM-SessionManagerRunShell',
                Reason='Remote Connection '
            )

        except self.ssmClient.exceptions.TargetNotConnected as err:
            logger.error(f'Target not connected: {err}')
            return None

        print (response)
        return 'TBD'





#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    SessionManager().StartSession('i-01a53f6433e3bd12e')

    # https://support.kraken.com/hc/en-us/articles/360043283472-Python-WebSocket-recommended-Python-library-and-usage-examples

    # oldRet= {
    #     'SessionId': 'phil-0b1ef84de610cbe5e',
    #     'TokenValue': 'AAEAAfCuy89CURdn3Vo2O1smaqiehEHsKi/YJXbApPuF+uqAAAAAAGImG63PlzJ8xWw0Da+Gpv7WR3GUfeuhRv8OrqdqS2bgUzyLoUP79TiVFj0LNkqJbVfbncg2a7pv7IWpXqj9iAtopF71X/ZcXSQmKncQxPK2NNcjdBV/XhpcOQ5/jKWyoys29XSCwSxUT5wb248ZGDJeb5fUsM1jm9hNxGc5dZIT7q21mlKN/BEuoA/4OtB0YPdXOPsbt3brseK0ZG5G7J7Ab6+BUvUxiI7MB3u5K1/cvjX+ioHeoxldXKOmwtqkEB5LIccJ/vSL+2Mtn9Ad8y2ulP32+D5ZJ+5wPEFpgaZxNHMoqAPS0cm82+Q6MTiD89vZOvteW+3wICP8qow4pVby+mDihgwD9hlA7dPaf+xXbobCPujmd/wKLqOIXcK+zA6j4LiSMw8J75QWEvDh9z3CPyycN3E8H6+bbxHE/ATggGOkq01rFbv5mCpIYSezSug/3jM=',
    #     'StreamUrl': 'wss://ssmmessages.ca-central-1.amazonaws.com/v1/data-channel/phil-0b1ef84de610cbe5e?role=publish_subscribe',
    #     'ResponseMetadata': {'RequestId': '7c9b80b7-e35e-43a8-b1ab-7a50292651d1', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Mon, 07 Mar 2022 14:50:21 GMT', 'content-type': 'application/x-amz-json-1.1', 'content-length': '683', 'connection': 'keep-alive', 'x-amzn-requestid': '7c9b80b7-e35e-43a8-b1ab-7a50292651d1'}, 'RetryAttempts': 0}}


    # Import WebSocket client library (and others)
    # import websocket
    # import _thread
    # import time

    # wssUrl = oldRet['StreamUrl']

    # handle = None
    # # Define WebSocket callback functions
    # def wsMessage(ws, message):
    #     print(f"WebSocket thread: {message}")

    # def wsOpen(ws):
    #     print("WebSocket Opens")
    #     # ws.send('\n')

    # def wsError(ws, error):
    #     print(f"WebSocket Error: {error}")

    # def wsClose(ws, close_status_code, close_msg):
    #     print(f"WebSocket Closing: {close_status_code} - {close_msg}")


    # def wsThread(*args):
    #     ws = websocket.WebSocketApp(
    #         wssUrl,
    #         on_open = wsOpen,
    #         on_message = wsMessage,
    #         on_error=wsError,
    #         on_close=wsClose
    #     )
    #     global handle
    #     handle = ws
    #     ws.run_forever()

    # # Start a new thread for the WebSocket interface
    # _thread.start_new_thread(wsThread, ())

    # # Continue other (non WebSocket) tasks in the main thread
    # while True:
    #     cmdInput = input('')
    #     if handle is not None:
    #         handle.send(cmdInput)
    #     else:
    #         print('Web Socket is not ready')


    # aws ssm start-session --target i-0a5bcdfd07f7e7940


