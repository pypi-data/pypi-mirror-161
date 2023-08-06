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
import pandas as pd
import o7lib.util.report
import o7lib.aws.sns
import o7lib.aws.base

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html

logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class Cloudwatch(o7lib.aws.base.Base):

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session=session)
        self.cwUsEast1 = self.session.client('cloudwatch', region_name='us-east-1')
        #self.cw = self.session.client('cloudwatch')


    #*************************************************
    #
    #*************************************************
    def ReportAlarmSnsEmail(self, report, name, namespace = "", metricName = "", minimum = 0):

        alarms = self.LoadAlarmsUsEast1()

        # Check for Event Rule
        report.AddTest(name=f"{name} Alarm Exist", critical=True)

        alarm = alarms[alarms['Namespace'] == namespace]
        alarm = alarm[alarm['MetricName'] == metricName]

        if len(alarm.index) == 0:
            report.TestFail('No Alarm')
            return report

        alm = alarm.iloc[0]
        almName = alm['AlarmName']
        report.TestPass(f'Alarm name {almName}')

        # Check it is enable
        report.AddTest(name=f"{name} Alarm Threshold", critical=True)
        threshold = alm['Threshold']


        if threshold > minimum : report.TestPass(f"{threshold}")
        else: report.TestFail(f'Too Low {threshold} < {minimum}')

        # Check it is enable
        report.AddTest(name=f"{name} Alarm is Enable", critical=True)
        if alm['ActionsEnabled'] == True : report.TestPass()
        else: report.TestFail(f'State is {alm["State"] }')


        # Check for SNS Target
        report.AddTest(name=f"{name} Alarm has an SNS Target", critical=True)
        actions = alm['AlarmActions']
        snsTargets = [s for s in actions if "arn:aws:sns:" in s]
        if len(snsTargets) == 0:
            report.TestFail('No SNS Target')
            return report

        arn = snsTargets[0]
        report.TestPass(f'Arn {arn}')

        # Check for Active Email Subcription
        report.AddTest(name=f"{name} Alarm has email subcription", critical=True)
        subs = o7lib.aws.sns.Sns(session=self.session, region='us-east-1').LoadSubcriptions(arn)
        subsEmail = subs[subs['Protocol'] == 'email']
        subsEmail = subsEmail[subsEmail['SubscriptionArn'].str.contains('arn:aws:sns:')]

        if len(subsEmail.index) == 0:
            report.TestFail('No Email Subcription')
            return report

        emails = ','.join(subsEmail['Endpoint'].tolist())
        report.TestPass(f'{emails}')



    #*************************************************
    #
    #*************************************************
    def LoadAlarmsUsEast1(self):

        # print(f"Getting All Event Rules")
        alarms = pd.DataFrame(columns = ['AlarmName', 'Namespace', 'MetricName', 'StateValue', 'AlarmActions', 'Threshold'])

        done=False
        param={ }

        while not done:

            resp = self.cwUsEast1.describe_alarms(**param)
            #pprint.pprint(resp)

            if 'NextToken' in resp: param['NextToken'] = resp['NextToken']
            else: done = True

            # Process all entries to store in Pandas dataframe
            for alarm in resp['MetricAlarms'] :
                alarms = alarms.append(alarm, ignore_index=True)

        #print(alarms)

        return alarms

#*************************************************
#
#*************************************************
if __name__ == "__main__":

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.width', 200)
    pd.set_option('display.max_colwidth', 20)

    r = o7lib.util.report.Report('Account Conformity Report', sectionName="CloudWatch")
    r = Cloudwatch().ReportAlarmSnsEmail(r, name = 'Billing', namespace='AWS/Billing', metricName='EstimatedCharges')

    #alarms = LoadAlarms()

    # pprint.pprint(rules[['Name','EventPattern']])

    # pprint.pprint(rules[rules['EventPattern'] == '{"source":["aws.guardduty"]}'])


