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
import pandas as pd
import datetime
import logging

import botocore.exceptions

import o7lib.aws.base
import o7lib.util.input
import o7lib.util.report
import o7lib.aws.cloudwatch

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

logger=logging.getLogger(__name__)


#*************************************************
#
#*************************************************
class CostExplorer(o7lib.aws.base.Base):
    """Class to Explore AWS costs"""

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session = session)
        self.ce = self.session.client('ce')



    #*************************************************
    #
    #*************************************************
    def ConformityReport(self, report=None):

        sectionName = 'Cost Explorer & Billing'
        r = report
        if r is None: r = o7lib.util.report.Report('Account Conformity Report', sectionName=sectionName)
        else: r.AddSection(sectionName)


        o7lib.aws.cloudwatch.Cloudwatch(session=self.session).ReportAlarmSnsEmail(r, name = 'Billing', namespace='AWS/Billing', metricName='EstimatedCharges')

        r.AddTest(name="Cost Explorer Status", critical=True)
        try: tags = self.ListTags()
        except botocore.exceptions.ClientError:
            r.TestFail("Not Enable in Account")
            return False

        r.TestPass("Enable")

        r.AddTest(name="Cost Explorer Tag", critical=True)
        if len(tags) == 0:
            r.TestFail("No Tags Found")
            return

        r.TestPass(f'Found {len(tags)} Tags')

        r.AddTest(name="Tag PROJECT created", critical=False)
        if 'PROJECT' in tags :
            r.TestPass()

        r.TestFail()


        return True

    #*************************************************
    #
    #*************************************************
    def LoadCosts(self, days=30, tagKey='PROJECT'):
        """Load Cost information"""

        now = datetime.datetime.now()
        dateStart = (now - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        dateEnd = now.strftime('%Y-%m-%d')

        logger.info(f"Getting AWS Cost from {dateStart} to {dateEnd} group by tag {tagKey}")
        costs = []
        ret =  pd.DataFrame()

        done=False
        param={
                'TimePeriod':{
                        'Start': dateStart,
                        'End': dateEnd
                },
                'Granularity' : 'DAILY',
                'Metrics' : ['NetAmortizedCost'],
                'GroupBy' : [
                    {'Type': 'DIMENSION','Key': 'USAGE_TYPE'},
                    {'Type': 'TAG', 'Key': tagKey}
                ]
        }

        while not done:

            resp = self.ce.get_cost_and_usage(**param)
            #pprint.pprint(resp)

            if 'NextPageToken' in resp: param['NextPageToken'] = resp['NextPageToken']
            else: done = True

            # Process all entries to store in Pandas dataframe
            for results in resp['ResultsByTime'] :

                strDay = results['TimePeriod']['Start']
                dtDay = datetime.datetime.strptime(strDay, "%Y-%m-%d")
                for g in results['Groups'] :

                    tags = g['Keys'][1].split('$')
                    tagValue='No Tag'
                    if len(tags) > 1: tagValue=tags[1]

                    line = {
                        "Date" : dtDay,
                        "Usage_Type" : g['Keys'][0],
                        tagKey : tagValue,
                        "Cost" : float(g['Metrics']['NetAmortizedCost']['Amount']),
                    }
                    costs.append(line)

        ret = pd.DataFrame(data = costs)
        return ret



    #*************************************************
    #
    #*************************************************
    def ListTags(self):

        # print(f"Getting AWS Cost Tags")
        now = datetime.datetime.now()
        dateStart = (now - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
        dateEnd = now.strftime('%Y-%m-%d')

        ret = []

        param={
                'TimePeriod':{
                        'Start': dateStart,
                        'End': dateEnd
                },
        }
        resp = self.ce.get_tags(**param)
        # pprint.pprint(resp)

        if 'Tags' in resp:
            for t in resp['Tags']: ret.append(t)

        return ret

    #*************************************************
    #
    #*************************************************
    def CompileCostbyGroup(self, costs, tagKey='PROJECT'):

        #-----------------------
        # Max number of days
        #-----------------------
        days = (datetime.datetime.now() - costs['Date'].min()).days
        logger.info(f'Compile for {days} days')
        d = {'Total': f'{days} Day Sum', 'Avr' : f'{days} Day Avr', 'Max' : f'{days} Day Max'}


        #-----------------------
        # Group By Days
        #-----------------------
        dailyCosts = costs.groupby(['Date',tagKey]).agg({'Cost':sum})
        dailyCosts = dailyCosts.fillna(0)
        #print(dailyCosts)

        #-----------------------
        # Compile on full range
        #-----------------------
        day30Costs = dailyCosts.groupby([tagKey]).agg(
            Total=('Cost','sum'),
            Max=('Cost','max')
        )
        day30Costs['Avr'] = day30Costs.Total / days
        day30Costs = day30Costs.rename(columns=d)

        #-----------------------
        # Compile on 7 days
        #-----------------------
        day7 = datetime.datetime.now() - datetime.timedelta(days=8)
        d = {'Total': '7 Day Sum', 'Avr' : '7 Day Avr'}

        day7Costs = dailyCosts.loc[day7:]
        day7Costs = day7Costs.groupby([tagKey]).agg(
            Total=('Cost','sum')
        )
        day7Costs['Avr'] = day7Costs.Total / 7
        day7Costs = day7Costs.rename(columns=d)

        #-----------------------
        # Compile on last day
        #-----------------------
        yesterday = datetime.datetime.now() - datetime.timedelta(days=2)

        d = {'Total': 'Yesterday'}
        yesterdayCosts = dailyCosts.loc[yesterday:]
        yesterdayCosts = yesterdayCosts.groupby([tagKey]).agg(
            Total=('Cost','sum')
        ).rename(columns=d)


        projectCosts = pd.concat([day30Costs, day7Costs, yesterdayCosts], axis=1, join="outer")
        projectCosts = projectCosts.reset_index()
        projectCosts = projectCosts.sort_values(by=['30 Day Sum'], ascending=False)

        return projectCosts


    #*************************************************
    #
    #*************************************************
    def DisplayProjectSummary(self, costs, tagKey='PROJECT'):

        print("-----------------------------")
        print(f"Cost Explore Summary - {self.TitleLine()}")
        print(f"Using cost TAG KEY: {tagKey}")
        print("-----------------------------")
        tagCosts = self.CompileCostbyGroup(costs, tagKey)
        print(tagCosts)
        print("-----------------------------")
        return tagCosts


    #*************************************************
    #
    #*************************************************
    def DisplayProjectDetails(self, costs, tagKey='PROJECT', tagValue=''):

        print("-----------------------------")
        print(f"Usage Type Details")
        print(f"Tag Key: {tagKey}  Tag Value: {tagValue}")
        print("-----------------------------")
        tagCosts=costs[costs[tagKey] == tagValue]
        compileCosts = self.CompileCostbyGroup(tagCosts, 'Usage_Type')
        print(compileCosts)
        print("-----------------------------")
        return compileCosts

    #*************************************************
    #
    #*************************************************
    def Menu(self):
        tagKey='PROJECT'
        costs = self.LoadCosts(tagKey=tagKey)

        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.float_format', '{:,.4f}'.format)  # https://docs.python.org/2/library/string.html#formatstrings

        while True :

            tagCosts = self.DisplayProjectSummary(costs, tagKey)
            t, key = o7lib.util.input.InputMulti('Option -> Exit(e), Change Tag(t), To Excel(x), Details(int): ')

            if t == 'str':
                if key.lower() == 'e': break
                if key.lower() == 't':
                    tagKey = o7lib.util.input.InputString('Input Tag Key :')
                    costs = self.LoadCosts(tagKey=tagKey)
                if key.lower() == 'l': self.ListTags()
                if key.lower() == 'x': costs.to_excel("aws-cost.xlsx")

            if t == 'int':
                tagValue = tagCosts.loc[key][tagKey]
                print(f"Getting Detailed for Tag Value: {tagValue}")
                self.DisplayProjectDetails(costs, tagKey=tagKey, tagValue=tagValue)
                o7lib.util.input.WaitInput()





#*************************************************
#
#*************************************************
if __name__ == "__main__":

    #CostExplorer().Menu()
    CostExplorer().ConformityReport()
    #print(f'List of tags: {ListTags()}')
