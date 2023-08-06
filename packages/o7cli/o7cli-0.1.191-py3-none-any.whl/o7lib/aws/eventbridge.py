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
import o7lib.aws.base
import o7lib.aws.sns


logger=logging.getLogger(__name__)

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events.html#cloudwatchevents


#*************************************************
#
#*************************************************
class Eventbridge(o7lib.aws.base.Base):

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session = session)
        self.cwe = self.session.client('events')

    #*************************************************
    #
    #*************************************************
    def ReportEventRuleSnsEmail(self, report, name, patterns = []):

        rules = self.LoadRules()

        # Check for Event Rule
        report.AddTest(name=f"{name} Event Exist", critical=True)

        gdRule = rules[rules['EventPattern'].isin(patterns)]

        if len(gdRule.index) == 0:
            report.TestFail('No Event Rule')
            return report

        gdName = gdRule.iloc[0]['Name']
        report.TestPass(f'Rule name {gdName}')

        # Check it is enable
        report.AddTest(name=f"{name} Event Rule is Enable", critical=True)
        if gdRule.iloc[0]['State'] == 'ENABLED' : report.TestPass()
        else: report.TestFail(f'State is {gdRule.iloc[0]["State"] }')


        # Check for SNS Target
        report.AddTest(name=f"{name} Event Rule has an SNS Target", critical=True)
        targets = self.LoadTargets(gdName)
        snsTargets = targets[targets['Arn'].str.contains("arn:aws:sns:")]
        if len(snsTargets.index) == 0:
            report.TestFail('No SNS Target')
            return report

        arn = snsTargets.iloc[0]['Arn']
        report.TestPass(f'Arn {arn}')

        # Check for Active Email Subcription
        report.AddTest(name=f"{name} Event Rule has email subcription", critical=True)
        subs = o7lib.aws.sns.Sns(session = self.session).LoadSubcriptions(arn)
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
    def LoadTargets(self, ruleName):

        #print(f"Getting Targets for Rule: {ruleName}")
        targets = pd.DataFrame(columns = ['Id','Arn'])

        done=False
        param={
            'Rule' : ruleName
        }

        while not done:

            resp = self.cwe.list_targets_by_rule(**param)
            #pprint.pprint(resp)

            if 'NextToken' in resp: param['NextToken'] = resp['NextToken']
            else: done = True

            # Process all entries to store in Pandas dataframe
            for target in resp['Targets'] :
                targets = targets.append(target, ignore_index=True)

        #print(targets)

        return targets


    #*************************************************
    #
    #*************************************************
    def LoadRules(self):

        # print(f"Getting All Event Rules")
        rules = pd.DataFrame(columns = ['Name', 'EventPattern', 'Arn', 'State'])

        done=False
        param={ }

        while not done:

            resp = self.cwe.list_rules(**param)
            # pprint.pprint(resp)

            if 'NextToken' in resp: param['NextToken'] = resp['NextToken']
            else: done = True

            # Process all entries to store in Pandas dataframe
            for rule in resp['Rules'] :
                rules = rules.append(rule, ignore_index=True)

        #print(rules)

        return rules

#*************************************************
#
#*************************************************
if __name__ == "__main__":

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', -1)

    r = o7lib.util.report.Report('Account Conformity Report', sectionName="Event Bridge")
    r = Eventbridge().ReportEventRuleSnsEmail(r, name = 'GuardDuty', patterns = ['{"source":["aws.guardduty"]}', '{"source":["aws.guardduty"],"detail-type":["GuardDuty Finding"]}'])

    #rules = LoadRules()

    # pprint.pprint(rules[['Name','EventPattern']])

    # pprint.pprint(rules[rules['EventPattern'] == '{"source":["aws.guardduty"]}'])


