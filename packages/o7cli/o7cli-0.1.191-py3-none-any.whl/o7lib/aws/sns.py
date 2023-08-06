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
import o7lib.aws.base

logger=logging.getLogger(__name__)

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html

#*************************************************
#
#*************************************************
class Sns(o7lib.aws.base.Base):

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session = session)
        self.sns = self.session.client('sns', region_name=region)


    #*************************************************
    #
    #*************************************************
    def LoadSubcriptions(self, arn):


        #print(f"Getting Subcription for Arn: {arn}")
        subs = pd.DataFrame(columns = ['Endpoint','Owner','Protocol','SubscriptionArn', 'TopicArn'])

        done=False
        param={
            'TopicArn' : arn
        }

        while not done:

            resp = self.sns.list_subscriptions_by_topic(**param)
            #pprint.pprint(resp)

            if 'NextToken' in resp: param['NextToken'] = resp['NextToken']
            else: done = True

            # Process all entries to store in Pandas dataframe
            for sub in resp['Subscriptions'] :
                subs = subs.append(sub, ignore_index=True)

        #print(targets)

        return subs

#*************************************************
#
#*************************************************
if __name__ == "__main__":

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 40)

    # subs = LoadSubcriptions('arn:aws:sns:ca-central-1:..... test arn')

    #print(subs)