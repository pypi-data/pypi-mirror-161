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


#--------------------------------
#
#--------------------------------
import logging
import o7lib.util.report
import o7lib.aws.base

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudtrail.html

logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class Cloudtrail(o7lib.aws.base.Base):

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session = session)
        self.ct = self.session.client('cloudtrail')


    #*************************************************
    #
    #*************************************************
    def ConformityReport(self, report=None):

        r = report
        if r is None: r = o7lib.util.report.Report('Account Conformity Report', sectionName="Cloud Trail")
        else: r.AddSection("Cloud Trail")

        resp = self.ct.describe_trails()
        #pprint.pprint(resp)

        r.AddTest(name="Global Trail present for account", critical=True)

        if 'trailList' not in resp:
            r.TestFail("No traiList in Response")
            return False

        if len(resp['trailList']) < 1:
            r.TestFail("No Trails for this account (recommend name: account-global-trail)")
            return False

        theTrail = None
        for t in resp['trailList'] :
            if t['IsMultiRegionTrail'] == True and t['IncludeGlobalServiceEvents'] == True : theTrail = t

        if theTrail is None :
            r.TestFail("No Global Trail found for this account")
            return False

        r.TestPass(f'{theTrail["Name"]}')

        r.AddTest(name="S3 bucket into which CloudTrail delivers your trail files", critical=True)
        if 'S3BucketName' in theTrail  : r.TestPass(theTrail['S3BucketName'])

        r.AddTest(name="Cloudwatch where logs are delivered", critical=True)
        if 'CloudWatchLogsLogGroupArn' in theTrail  : r.TestPass(theTrail['CloudWatchLogsLogGroupArn'])

        r.AddTest(name="Log file validation is enabled", critical=True)
        if theTrail['LogFileValidationEnabled'] == True : r.TestPass()


        r.TestFail()


        return True


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    Cloudtrail().ConformityReport()