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
import o7lib.util.report
import o7lib.aws.base
import o7lib.aws.eventbridge

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/guardduty.html

logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class Guardduty(o7lib.aws.base.Base):

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session = session)
        self.gd = self.session.client('guardduty')


    #*************************************************
    #
    #*************************************************
    def ConformityReport(self, report=None):

        r = report
        if r is None: r = o7lib.util.report.Report('Account Conformity Report', sectionName="Guard Duty")
        else: r.AddSection("Guard Duty")

        resp = self.gd.list_detectors()

        r.AddTest(name="Detector present for account", critical=True)

        if 'DetectorIds' not in resp:
            r.TestFail("No DetectorIds in record")
            return False

        if len(resp['DetectorIds']) < 1:
            r.TestFail("No Detector for this account")
            return False

        if len(resp['DetectorIds']) > 1:
            r.TestFail("Found Multiple Detectors for this account, unexpected !")
            return False

        d = resp['DetectorIds'][0]
        r.TestPass(f'id {d}')

        resp = self.gd.get_detector(DetectorId=d)
        #pprint.pprint(resp)

        r.AddTest(name="Service Enable", critical=True)
        if 'Status' in resp and resp["Status"] == 'ENABLED' : r.TestPass()

        r.AddTest(name="Source - CloudTrail Enable", critical=True)
        if 'DataSources' in resp and resp["DataSources"]["CloudTrail"]["Status"] == 'ENABLED' : r.TestPass()

        r.AddTest(name="Source - DNSLogs Enable", critical=True)
        if 'DataSources' in resp and resp["DataSources"]["DNSLogs"]["Status"] == 'ENABLED' : r.TestPass()

        r.AddTest(name="Source - FlowLogs Enable", critical=True)
        if 'DataSources' in resp and resp["DataSources"]["FlowLogs"]["Status"] == 'ENABLED' : r.TestPass()

        r.AddTest(name="Source - S3Logs Enable", critical=True)
        if 'DataSources' in resp and resp["DataSources"]["S3Logs"]["Status"] == 'ENABLED' : r.TestPass()


        r.AddTest(name="Findings Exported to S3", critical=True)

        resp = self.gd.list_publishing_destinations(DetectorId=d)
        #pprint.pprint(resp)

        if 'Destinations' in resp and  len(resp["Destinations"]) > 0 :
            for d in resp["Destinations"] :
                if d["DestinationType"] == 'S3' and d["Status"] == 'PUBLISHING':
                    r.TestPass()

        r.TestFail("Not Enable (recommended S3 Name: aws-guardduty-logs-<accountId>")

        r = o7lib.aws.eventbridge.Eventbridge(session=self.session).ReportEventRuleSnsEmail(
            report=r, name = 'GuardDuty',
            patterns = ['{"source":["aws.guardduty"]}', '{"source":["aws.guardduty"],"detail-type":["GuardDuty Finding"]}'])


        # Get $ usage per Datasource
        #resp = gd.get_usage_statistics(DetectorId=d,UsageStatisticType='SUM_BY_DATA_SOURCE', UsageCriteria={'DataSources':['FLOW_LOGS','CLOUD_TRAIL','DNS_LOGS','S3_LOGS']})
        #pprint.pprint(resp)


        return True


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    Guardduty().ConformityReport()