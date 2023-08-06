
#!/usr/bin/python3
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
import os
import boto3
import json

#*************************************************
# Reformat SNS Message to a SMS consumable texte
#*************************************************
def ReformatForSMS(snsMessage):

    theMsg = ""

    # ----------------------------
    # ALARM Event - Rewrite for clear SMS
    # ----------------------------
    if 'AlarmDescription' in snsMessage :
        theMsg = snsMessage['AlarmDescription'] + "\n"
        theMsg += 'State: ' + snsMessage['NewStateValue'] + "\n"
        theMsg += 'Since: ' + snsMessage['StateChangeTime']

    # ----------------------------
    # Guard duty Event
    # ----------------------------
    if snsMessage['source'] == "aws.guardduty":

        theType = snsMessage["detail-type"]

        if theType == 'GuardDuty Finding' :
            theMsg = theType + '\n'
            theMsg += snsMessage['detail']['description']

        elif theType == 'AWS API Call via CloudTrail' :
            theMsg = 'GuardDuty API' + '\n'
            theMsg += snsMessage['detail']['eventName'] + '\n'
            theMsg += 'By ' + snsMessage['detail']['userIdentity']['userName']
        else:
            theMsg = theType + '\n'
            theMsg = 'New Guarduty Type'

    return theMsg

#*************************************************
# Function that can transmit a Event to another region that can send SMS.
#*************************************************
def TransmitToSmsTopic (snsEvent, arnSmsTopic):

    #print(f'TransmitToSms snsEvent: {snsEvent}')
    rawSnsMessage = snsEvent["Message"]
    jsonSnsMessage = json.loads(rawSnsMessage)

    #print(f'Complete Sns Message:')
    #pprint.pprint(jsonSnsMessage)

    theMsg = ReformatForSMS(jsonSnsMessage)
    print(f'Reformat Sms Message: {theMsg}')

    sns = boto3.client(service_name='sns', region_name='us-east-1')

    params = {
        'Message': theMsg,
        'Subject': snsEvent['Subject'],
        'TopicArn': arnSmsTopic
    }
    if params['Subject'] is None: params['Subject'] = 'No Subject'
    #pprint.pprint(params)

    resp = sns.publish(**params)
    print(f'sns.publish response: {resp}')

#*************************************************
#
#*************************************************
def TransmitToSms_handler(event, context):

    arnSmsTopic = os.environ.get('ARN_SMS_TOPIC', None)
    if arnSmsTopic is None:
        print('[ERROR] Environement Variable ARN_SMS_TOPIC is missing')
        return {'statusCode': 401,'body': json.dumps('Environement Variable ARN_SMS_TOPIC is missing')}


    #print(f'Handler Event {event}')
    theSns = event['Records'][0]['Sns']
    TransmitToSmsTopic(theSns, arnSmsTopic = arnSmsTopic)

    return {
        'statusCode': 200,
        'body': json.dumps('Done')
    }
