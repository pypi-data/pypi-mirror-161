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
"""Module for AWS useful class"""

import datetime
import logging
import boto3


import o7lib.util.terminal

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html

logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class Base():
    """Basic class for all the AWS Class"""

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):

        self.session = session

        # https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html

        if self.session is None:
            logger.info(f'Creation new sessions with: profile -> {profile} region -> {region}')

            self.session = boto3.session.Session(profile_name = profile, region_name = region)
        else:
            logger.info(f'Using Existing session with : profile -> {self.session.profile_name} region -> {self.session.region_name}')



    def TitleLine(self): # TBR
        """Return a string with Region & Profile; useful for titles"""

        return f'Region: {self.session.region_name} - Profile: {self.session.profile_name}'

    def SessionInfo(self):
        """Return a string with Region & Profile; useful for titles"""

        return f'Region: {self.session.region_name} - Profile: {self.session.profile_name}'

    def ConsoleTitle(self, left = "", center = ""):
        """Clear Console & add Specific Title"""
        if len(center) == 0:
            center = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%Sz')

        o7lib.util.terminal.ConsoleTitle(left = left, center=center, right=self.SessionInfo())
