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

import o7lib.aws.base

logger=logging.getLogger(__name__)

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sts.html


#*************************************************
#
#*************************************************
class Sts(o7lib.aws.base.Base):

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session = session)
        self.sts = self.session.client('sts')

    #*************************************************
    #
    #*************************************************
    def GetAccountId(self):

        resp = self.sts.get_caller_identity()
        ret = resp.get('Account')
        return ret

#*************************************************
#
#*************************************************
if __name__ == "__main__":
    print(f"Account Id = {Sts().GetAccountId()}")
    # boto3.client('iam').list_account_aliases()['AccountAliases']
    # id = boto3.client('sts').get_caller_identity().get('Account')
    # name =   boto3.client('organizations').describe_account(AccountId=id).get('Account').get('Name')
