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
"""Module for O7 Command Line Interface"""

#--------------------------------
#
#--------------------------------
import sys
import getopt
import logging
import pkg_resources

import botocore

import o7lib.aws.reports
import o7lib.aws.costexplorer
import o7lib.aws.cloudformation
import o7lib.aws.ec2
import o7lib.aws.ecs
import o7lib.aws.s3
import o7lib.aws.asg
import o7lib.aws.cloudmap
import o7lib.aws.lambdafct
import o7lib.aws.rds
import o7lib.aws.pipeline
import o7lib.aws.codebuild
import o7lib.aws.codecommit
import o7lib.aws.logs
import o7lib.version
import o7lib.util.pypi
import o7lib.util.displays


logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
def Help():
    """Print help information"""
    print ('o7 [options] <module>')
    print ('Useful CLI and scripts for O7 Conseils DevOps practice')
    print (f'version: {o7lib.version.VERSION_ID}')
    print ('Options:')
    print ('    -p <profile> : Set AWS Profile')
    print ('    -r <region>  : Set AWS Region')
    print ('    -d           : Set DEBUG Traces')
    print ('    -v           : Version Number')
    print ('Available Modules:')
    print ('    report: Multiple Reports')
    print ('    cost: Analyse AWS Sccount Cost')
    print ('    log: Cloudwatch Logs')
    print ('    cm: Cloud Map ')
    print ('')
    print ('    s3: S3 (Simple Scalable Storage)')
    print ('    ec2: Elastic Computing ')
    print ('    ecs: Elastic Container Service ')
    print ('    lf: Lambda Funcition ')
    print ('    rds: Relational DB ')
    print ('    asg: Auto Scaling Group ')
    print ('')
    print ('    cfn: Cloudformation ')
    print ('    pl: Code Pipeline')
    print ('    cb: Code Build')
    print ('    cc: Code Commit')

    sys.exit(2)


#*************************************************
#
#*************************************************
def CredentialHelp():
    """Print help about credential issues"""
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration
    print('There are different way to configure your AWS credentials')
    print('ref: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration')
    print('')
    print('- If you have the AWS CLI install, use -> aws configure')
    print('- Else, create your own credential file (see ref link)')
    print('')
    print('Note: o7 supports the usage of multiple profile, option -p')
    print('')


#*************************************************
#
#*************************************************
def VersionVerification():
    """Verify if runngin latest version and notify accordingly"""

    lastestVersion = o7lib.util.pypi.Pypi(project='o7cli').GetLatestVersion()

    if o7lib.version.VERSION_ID == 'LOCAL_VERSION':
        o7lib.util.displays.PrintWarning(f'You are using a LOCAL VERSION, latest release is {lastestVersion}')

    elif lastestVersion is not None:
        if pkg_resources.parse_version(lastestVersion) > pkg_resources.parse_version(o7lib.version.VERSION_ID):
            o7lib.util.displays.PrintWarning(f'You are using version o7cli {o7lib.version.VERSION_ID}, however, version {lastestVersion} is available.')
            o7lib.util.displays.PrintWarning("Please consider upgrading via the 'pip install --upgrade o7cli' command.")

#*************************************************
#
#*************************************************
def CommandLine(argv):
    """Main Menu for CLI"""

    VersionVerification()

    # https://docs.python.org/3.1/library/getopt.html
    try:
        opts, args = getopt.getopt(argv,"vdp:r:", [])
    except getopt.GetoptError:
        Help()

    param = {
        'profile' : None,
        'region' : None
    }

    for opt, arg in opts:
        if opt == '-p':
            print(f'Setting default profile to : {arg}')
            param['profile'] = arg

        if opt == '-v':
            print(f'{o7lib.version.VERSION_ID}')
            sys.exit(0)

        if opt == '-r':
            print(f'Setting Region to : {arg}')
            param['region'] = arg

        if opt == '-d':
            print('Setting debug mode')
            logging.basicConfig(
                level=logging.DEBUG,
                format="[%(levelname)-5.5s] [%(name)s] %(message)s"
            )


    if len(args) < 1:
        Help()

    module = args[0]

    logger.info("Going to module: %s", module)

    try:

        if module == 'report':
            o7lib.aws.reports.Report(**param).Run('conformity')
        elif module == 'cost':
            o7lib.aws.costexplorer.CostExplorer(**param).Menu()
        elif module == 'cf':
            o7lib.aws.cloudformation.Cloudformation(**param).MenuStacks()
        elif module == 'lf':
            o7lib.aws.lambdafct.Lambda(**param).MenuFunctions()
        elif module == 's3':
            o7lib.aws.s3.S3(**param).MenuBuckets()
        elif module == 'ec2':
            o7lib.aws.ec2.Ec2(**param).MenuInstances()
        elif module == 'ecs':
            o7lib.aws.ecs.Ecs(**param).MenuClusters()
        elif module == 'asg':
            o7lib.aws.asg.Asg(**param).MenuAutoScalingGroups()
        elif module == 'rds':
            o7lib.aws.rds.Rds(**param).MenuInstances()
        elif module == 'cm':
            o7lib.aws.cloudmap.CloudMap(**param).MenuNamespaces()
        elif module == 'pl':
            o7lib.aws.pipeline.Pipeline(**param).MenuPipelines()
        elif module == 'cb':
            o7lib.aws.codebuild.CodeBuild(**param).MenuProjects()
        elif module == 'cc':
            o7lib.aws.codecommit.CodeCommit(**param).MenuRepos()
        elif module == 'log':
            o7lib.aws.logs.Logs(**param).MenuLogGroups()
        #elif (module == 'menu'): o7lib.menu.Menu()
        else:
            Help()

    except botocore.exceptions.NoRegionError:
        o7lib.util.displays.PrintError('ERROR! No AWS default region found')
        print('')
        print ("use -r option OR set an AWS Default Region ('export AWS_DEFAULT_REGION=ca-central-1') ")

    except botocore.exceptions.NoCredentialsError:
        o7lib.util.displays.PrintError('ERROR! No AWS credential found')
        print('')
        CredentialHelp()

    except botocore.exceptions.ProfileNotFound:
        o7lib.util.displays.PrintError('ERROR! Profile do not exist')

    except KeyboardInterrupt:

        print (f'{o7lib.util.displays.Colors.ENDC}\nGoodby...')



#*************************************************
#
#*************************************************
# def OldMenu(session):

#     accountId = o7lib.aws.sts.GetAccountId()
#     profile = o7lib.aws.session.GetProfile()
#     region = o7lib.aws.session.GetRegion()

#     while True :
#         print ('-' * 25)
#         print ('O7 Main Menu')
#         print (f'Local Profile: {profile}')
#         print (f'Account Id: {accountId}')
#         print (f'Region: {region}')
#         print ('-' * 25)
#         print ('1 - AWS Conformity Report')
#         print ('2 - AWS Cost Explorer Menu')
#         print ('-' * 25)

#         t, key = o7lib.util.input.InputMulti('Option: Exit(e), Selection(int)')
#         if t == 'str' and key.lower() == 'e': break
#         if t == 'int':
#             if key == 1: o7lib.aws.reports.Run('conformity')
#             if key == 2:  o7lib.aws.costexplorer.Menu()

#*************************************************
#
#*************************************************
def Main():
    """Callable from Script"""
    CommandLine(sys.argv[1:])


#*************************************************
#
#*************************************************
if __name__ == "__main__":
    CommandLine(sys.argv[1:])
