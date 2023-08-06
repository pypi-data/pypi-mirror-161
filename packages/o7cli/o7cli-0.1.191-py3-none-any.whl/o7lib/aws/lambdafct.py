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
"""Module allows to view and access Lambda Functions"""

#--------------------------------
#
#--------------------------------
import logging
#import datetime
import pprint

import o7lib.util.input
import o7lib.util.table
import o7lib.aws.base
import o7lib.aws.logs


logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class Lambda(o7lib.aws.base.Base):
    """Class for Cloudformation Stacks for a Profile & Region"""
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None):
        super().__init__(profile=profile, region=region)
        self.client = self.session.client('lambda')



    #*************************************************
    #
    #*************************************************
    def LoadFunctions(self):
        """Returns all Functions this Session"""

        logger.info('LoadFunctions')

        ret = []
        params={}


        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.list_functions
            response = self.client.list_functions(**params)
            #pprint.pprint(response)

            if 'NextMarker' in response:
                params['Marker '] = response['NextMarker']
            else:
                done = True

            logger.info(f'LoadFunctions: Number of Functions found {len(response["Functions"])}')
            for function in response['Functions'] :
                ret.append(function)

        return ret

    #*************************************************
    #
    #*************************************************
    def LoadFunctionInfo(self, name):
        """Returns Function details this Session"""

        logger.info(f'LoadFunctionInfo {name=}')
        ret = None


        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.get_function
        response = self.client.get_function(FunctionName=name)
        #response = self.client.get_function_configuration(FunctionName=name)
        #pprint.pprint(response)
        if 'Configuration' in response:
            ret = {}
            ret['Configuration'] = response['Configuration']
            ret['Code'] = response.get('Code',{})
            ret['Tags'] = response.get('Tags',{})
            ret['Concurrency'] = response.get('Concurrency',{})


        return ret
    #*************************************************
    #
    #*************************************************
    def DisplayFunctions(self, functions):
        """Displays a summary of Functions in a Table Format"""

        self.ConsoleTitle(left='Lambda Functions')
        print('')

        params = {
            'columns' : [
                {'title' : 'id'      , 'type': 'i',       'minWidth' : 4  },
                {'title' : 'Name'    , 'type': 'str',  'dataName': 'FunctionName'},
                {'title' : 'Updated' , 'type': 'str',  'dataName': 'LastModified'},
                {'title' : 'Runtime'  , 'type': 'str',  'dataName': 'Runtime'},
                {'title' : 'Description'  , 'type': 'str',  'dataName': 'Description', 'maxWidth' : 50}
            ]
        }
        o7lib.util.table.Table(params, functions).Print()


    #*************************************************
    #
    #*************************************************
    def DisplayFunction(self, funcInfo):
        """Displays a details of a functions """

        self.ConsoleTitle(left=f'Lambda Function {funcInfo["Configuration"]["FunctionName"]}')
        print('')
        pprint.pprint(funcInfo)


    #*************************************************
    #
    #*************************************************
    def MenuFunction(self, name):
        """Menu to view and edit all functions in current region"""

        while True :

            funcInfo = self.LoadFunctionInfo(name)
            self.DisplayFunction(funcInfo)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Logs(l): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'r':
                    pprint.pprint(funcInfo)
                    o7lib.util.input.WaitInput()

                if  key.lower() == 'l':
                    o7lib.aws.logs.Logs(session=self.session).MenuLogStreams(f'/aws/lambda/{name}')



    #*************************************************
    #
    #*************************************************
    def MenuFunctions(self):
        """Menu to view and edit all functions in current region"""

        while True :

            functions = self.LoadFunctions()
            self.DisplayFunctions(functions)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Details(int): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'r':
                    pprint.pprint(functions)
                    o7lib.util.input.WaitInput()

            if keyType == 'int' and 0 < key <= len(functions):
                print(f"Printing detailled for stack id: {key}")
                self.MenuFunction(name=functions[key-1]['FunctionName'])




#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    Lambda().MenuFunctions()
