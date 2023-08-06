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
"""Module allows to view and access CodeCommit"""

#--------------------------------
#
#--------------------------------
import logging
import pprint
import uuid

import o7lib.util.input
import o7lib.util.displays
import o7lib.aws.base

logger=logging.getLogger(__name__)


#*************************************************
#
#*************************************************
class CodeCommit(o7lib.aws.base.Base):
    """Class for Codecommit for a Profile & Region"""
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session=session)
        self.ccClient = self.session.client('codecommit')



    #*************************************************
    #
    #*************************************************
    def LoadRepos(self, repoName = None):
        """Returns all Repos for this Session"""

        logger.info('LoadRepos')

        repositoryNames = []
        repos = []
        param={}

        if repoName is None:
            done=False
            while not done:


                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.list_repositories
                resp = self.ccClient.list_repositories(**param)
                #pprint.pprint(resp)

                if 'nextToken' in resp:
                    param['nextToken'] = resp['nextToken']
                else:
                    done = True

                logger.info(f'LoadRepos: Number of Repos found {len(resp["repositories"])}')
                if len(resp["repositories"]) == 0:
                    break

                for repositorie in resp["repositories"]:
                    repositoryNames.append(repositorie['repositoryName'])

        else:
            repositoryNames.append(repoName)

        respDetails = self.ccClient.batch_get_repositories(repositoryNames = repositoryNames)
        # # pprint.pprint(respDetails)
        repos += respDetails["repositories"]

        return repos


    #*************************************************
    #
    #*************************************************
    def LoadBranches(self, repoName):
        """Returns all Branches for this Repo"""

        logger.info(f'LoadBranches {repoName=}')

        brancheIds = []
        branches = []
        param={
            'repositoryName' : repoName
        }

        # Load all Branch Ids
        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.list_branches
            resp = self.ccClient.list_branches(**param)
            # pprint.pprint(resp); o7lib.util.input.WaitInput()

            if 'nextToken' in resp:
                param['nextToken'] = resp['nextToken']
            else:
                done = True

            logger.info(f'LoadBranches: Number of Branches found {len(resp["branches"])}')
            brancheIds += resp["branches"]

        # Get details of all PRs
        for bId in brancheIds:
            # Takes too long respDetails = self.ccClient.get_branch(repositoryName = repoName, branchName = bId)
            branches.append({'branchName': bId})

        return branches

    #*************************************************
    #
    #*************************************************
    def LoadPullRequests(self, repoName = None, pullRequestId = None):
        """Returns all Branches for this Repo"""

        logger.info(f'LoadPullRequests {repoName=} {pullRequestId=}')

        prs = []
        prIds = []
        param={
            'repositoryName' : repoName,
            'pullRequestStatus' : 'OPEN'
        }

        if pullRequestId is not None:
            prIds += [pullRequestId]

        # Load all PR Ids
        done=False
        while repoName is not None and not done:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.list_pull_requests
            resp = self.ccClient.list_pull_requests(**param)
            #pprint.pprint(resp)

            if 'nextToken' in resp:
                param['nextToken'] = resp['nextToken']
            else:
                done = True

            logger.info(f'LoadPullRequests: Number of Pull Request found {len(resp["pullRequestIds"])}')
            if len(resp["pullRequestIds"]) == 0:
                break

            prIds += resp["pullRequestIds"]

        # Get details of all PRs
        for prId in prIds:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.get_pull_request
            # logger.info(f'LoadPullRequests details for {prId=}')
            respDetails = self.ccClient.get_pull_request(pullRequestId = prId)
            prDetails = respDetails['pullRequest']

            # only get extra details when a specific Pr is is provided
            if pullRequestId is not None:
                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.get_pull_request_approval_states
                respApprovals = self.ccClient.get_pull_request_approval_states(pullRequestId = prId, revisionId=prDetails['revisionId'] )
                prDetails['approvals'] = respApprovals['approvals']

                respOverride = self.ccClient.get_pull_request_override_state(pullRequestId = prId, revisionId=prDetails['revisionId'] )
                prDetails['override'] = {
                    'overridden' : respOverride.get('overridden', False),
                    'overrider'  : respOverride.get('overrider', "")
                }

                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.evaluate_pull_request_approval_rules
                respEval = self.ccClient.evaluate_pull_request_approval_rules(pullRequestId = prId, revisionId=prDetails['revisionId'] )
                prDetails['evaluation'] = respEval['evaluation']


            prs.append(prDetails)

        # reprocess some values
        for pullR in prs:
            if len(pullR.get('pullRequestTargets', [])) > 0:
                pullR['target'] = pullR['pullRequestTargets'][0]
                pullR['branchName'] = pullR['target']['sourceReference'].split('/')[-1]

            pullR['author'] = pullR['authorArn'].split('/')[-1]

        return prs


    #*************************************************
    #
    #*************************************************
    def LoadComments(self, pullRequestId):
        """Returns all Comments for this PullRequest"""

        logger.info(f'LoadComments {pullRequestId=}')

        comments = []
        param={
            'pullRequestId' : pullRequestId
        }

        # Load all PR Ids
        done=False
        while not done:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.get_comments_for_pull_request
            resp = self.ccClient.get_comments_for_pull_request(**param)
            #pprint.pprint(resp)

            if 'nextToken' in resp:
                param['nextToken'] = resp['nextToken']
            else:
                done = True

            for commentsForPrData in resp['commentsForPullRequestData']:
                comments += commentsForPrData.get('comments',[])

        logger.info(f'LoadComments: Number of comments found {len(comments)}')
        return comments


    #*************************************************
    #
    #*************************************************
    def LoadDifferences(self, repoName, afterCommit, beforeCommit):
        """Returns all Differences """

        logger.info(f'LoadDifferences {repoName=}')

        differences = []
        param={
            'repositoryName': repoName,
            'beforeCommitSpecifier': beforeCommit,
            'afterCommitSpecifier': afterCommit
        }

        # Load all PR Ids
        done=False
        while not done:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.get_differences
            resp = self.ccClient.get_differences(**param)
            #pprint.pprint(resp)

            if 'nextToken' in resp:
                param['nextToken'] = resp['nextToken']
            else:
                done = True

            differences += resp.get('differences',[])


        for difference in differences :

            before =  difference.get('beforeBlob', None)
            if before is not None:
                respBlob = self.ccClient.get_blob(repositoryName=repoName, blobId=before['blobId'])
                content = respBlob.get('content',b"").decode("utf-8")
                #print(content)
                difference['beforeBlob']['content'] = content
                difference['beforeBlob']['lineCount'] = content.count( "\n" ) + 1
                difference['path'] = before.get('path','NA')

            after =  difference.get('afterBlob', None)
            if after is not None:
                respBlob = self.ccClient.get_blob(repositoryName=repoName, blobId=after['blobId'])
                content = respBlob.get('content',b"").decode("utf-8")
                #print(content)
                difference['afterBlob']['content'] = content
                difference['afterBlob']['lineCount'] = content.count( "\n" ) + 1
                difference['path'] = after.get('path','NA')


        logger.info(f'LoadDifferences: Number of comments found {len(differences)}')
        return differences


    #*************************************************
    #
    #*************************************************
    def CreatePullRequest(self, repoName, destination):
        """Allow to create a Pull Request from terminal"""

        print('=' * 50)
        print('Pull Request Creation')
        print('=' * 50)

        branches = self.LoadBranches(repoName=repoName)
        paramBranch = {
            'columns' : [
                {'title' : 'id', 'type': 'i'},
                {'title' : 'Branch Name' , 'type': 'str', 'dataName': 'branchName'}
            ]
        }
        o7lib.util.displays.Table(paramBranch, branches)
        bId = o7lib.util.input.InputInt('Enter id of branch to merge : ')
        if bId < 1 or bId > len(branches):
            o7lib.util.displays.PrintError('Invalid branch Id')
            return

        title = o7lib.util.input.InputString('Enter title : ')
        description = o7lib.util.input.InputString('Enter description : ')
        source = branches[bId-1]['branchName']

        print('-' * 50)
        print('PULL REQUEST SUMMARY')
        print(f'Source Branch: {source}')
        print(f'Destination Branch: {destination}')
        print(f'Title: {title}')
        print(f'Description: {description}')
        print('-' * 50)

        isOk = o7lib.util.input.IsItOk('Confirm you want to create this Pull Request')
        if not isOk:
            return

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.create_pull_request
        response = self.ccClient.create_pull_request(
            title=title,
            description=description,
            targets=[
                {
                    'repositoryName': repoName,
                    'sourceReference': source,
                    'destinationReference': destination
                },
            ],
            clientRequestToken=str(uuid.uuid1())
        )

        print('Pull Request Creation Response ->')
        pprint.pprint(response)
        o7lib.util.input.WaitInput()


    #*************************************************
    #
    #*************************************************
    def MergePullRequest(self, pullRequestId):
        """Allow to merge from terminal"""

        pullRequest = self.LoadPullRequests(pullRequestId=pullRequestId)[0]

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.get_merge_options
        respMergeOptions = self.ccClient.get_merge_options(
            repositoryName=pullRequest['target']['repositoryName'],
            sourceCommitSpecifier=pullRequest['target']['sourceCommit'],
            destinationCommitSpecifier=pullRequest['target']['destinationReference'],
            conflictResolutionStrategy='NONE'
        )
        mergeOptions = respMergeOptions['mergeOptions']

        print('=' * 50)
        print('Pull Request Merge Validation')
        print('=' * 50)

        print('Possible Merge:')
        isFFM = 'FAST_FORWARD_MERGE' in mergeOptions
        isSM = 'SQUASH_MERGE' in mergeOptions
        isTWM = 'THREE_WAY_MERGE' in mergeOptions

        if not isFFM and not isSM and not isTWM:
            o7lib.util.displays.PrintError('Merge Conflict.... Resolve conflict first')
            o7lib.util.input.WaitInput()
            return

        o7lib.util.displays.PrintParamOk('1 - Fast Forward Merge', isFFM, isFFM )
        o7lib.util.displays.PrintParamOk('2 - Squash Merge', isSM, isSM )
        o7lib.util.displays.PrintParamOk('3 - Three Way Merge', isTWM, isTWM )
        print('<Other> - Back ')

        mergeId = o7lib.util.input.InputInt('Enter Desired Merge : ')

        if mergeId == 1 and isFFM:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.merge_pull_request_by_fast_forward
            isOk = o7lib.util.input.IsItOk('Confirm you want to make a Fast Forward Merge')
            if not isOk:
                return

            respMerge =  self.ccClient.merge_pull_request_by_fast_forward(
                pullRequestId=pullRequestId,
                repositoryName=pullRequest['target']['repositoryName']
            )

        elif mergeId == 2 and isSM:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.merge_pull_request_by_fast_forward
            isOk = o7lib.util.input.IsItOk('Confirm you want to make a Squashd Merge')
            if not isOk:
                return

            respMerge =  self.ccClient.merge_pull_request_by_squash(
                pullRequestId=pullRequestId,
                repositoryName=pullRequest['target']['repositoryName']
            )

        elif mergeId == 3 and isTWM:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.merge_pull_request_by_fast_forward
            isOk = o7lib.util.input.IsItOk('Confirm you want to make a Three Way Merge')
            if not isOk:
                return

            respMerge =  self.ccClient.merge_pull_request_by_three_way(
                pullRequestId=pullRequestId,
                repositoryName=pullRequest['target']['repositoryName']
            )

        else:
            return

        print('Merge Response ->')
        pprint.pprint(respMerge)

        prStatus = respMerge['pullRequest']['pullRequestStatus']

        if prStatus == 'CLOSED':
            isOk = o7lib.util.input.IsItOk('Do you want to delete branch ?')
            if isOk:
                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.delete_branch
                respDelete = self.ccClient.delete_branch(
                    repositoryName=pullRequest['target']['repositoryName'],
                    branchName=pullRequest['branchName'],
                )
                print('Delete Response ->')
                pprint.pprint(respDelete)

        o7lib.util.input.WaitInput()


    #*************************************************
    #
    #*************************************************
    def OverrideApproval(self, pullRequestId):
        """Allow to override approval """

        pullRequest = self.LoadPullRequests(pullRequestId=pullRequestId)[0]

        print('=' * 50)
        print('Approval Override Validation')
        print('=' * 50)


        isOk = o7lib.util.input.IsItOk('Do you really want to override the approval ?')
        if not isOk:
            return

        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html#CodeCommit.Client.override_pull_request_approval_rules
        resp = self.ccClient.override_pull_request_approval_rules(
            pullRequestId=pullRequestId,
            revisionId=pullRequest['revisionId'],
            overrideStatus='OVERRIDE'
        )

        print('Override Response ->')
        pprint.pprint(resp)

        o7lib.util.input.WaitInput()

    #*************************************************
    #
    #*************************************************
    def DisplayRepos(self, repos):
        """Displays a summary of Repos in a Table Format"""
        self.ConsoleTitle(left='CodeCommit Repositories List')
        print('')
        params = {
            'columns' : [
                {'title' : 'id'      , 'type': 'i',       'minWidth' : 4  },
                {'title' : 'Name'    , 'type': 'str',  'dataName': 'repositoryName'},
                {'title' : 'Created', 'type': 'date', 'dataName': 'creationDate'},
                {'title' : 'Updated', 'type': 'since', 'dataName': 'lastModifiedDate'},
                {'title' : 'Default', 'type': 'str', 'dataName': 'defaultBranch'},
                {'title' : 'Description' , 'type': 'str', 'dataName': 'repositoryDescription'},
            ]
        }
        o7lib.util.displays.Table(params, repos)


    #*************************************************
    #
    #*************************************************
    def DisplayPullRequestDetails(self, pullRequest, comments):
        """Displays a summary of a pull Request"""

        self.ConsoleTitle(left=f'CodeCommit Pull Request Id : {pullRequest["pullRequestId"]}')

        print('')
        print(f'Title: {pullRequest["title"]}')
        print('')
        print(f'Author: {pullRequest["authorArn"]}')
        print(f'Merge Status: {pullRequest["target"]["mergeMetadata"]}')
        print(f'Repository: {pullRequest["target"]["repositoryName"]}')
        print(f'Source Ref: {pullRequest["target"]["sourceReference"]}')
        print('')
        print(f'Approved: {pullRequest["evaluation"]["approved"]}')
        print(f'Overriden: {pullRequest["evaluation"]["overridden"]}')

        print('')
        print('List of comments')
        paramComments = {
            'columns' : [
                {'title' : 'id'      , 'type': 'i'},
                {'title' : 'Created'  , 'type': 'datetime',  'dataName': 'creationDate'},
                {'title' : 'Modified'  , 'type': 'since',  'dataName': 'lastModifiedDate'},
                {'title' : 'Content', 'type': 'str', 'dataName': 'content'}
            ]
        }
        o7lib.util.displays.Table(paramComments, comments)
        #pprint.pprint(branches)
        print('')



    #*************************************************
    #
    #*************************************************
    def DisplayReposDetails(self, repo, branches, pullRequests):
        """Displays a summary of Repos in a Table Format"""

        self.ConsoleTitle(left=f'CodeCommit Repositorie: {repo["repositoryName"]}')
        #pprint.pprint(repo)
        print('')
        print(f'Default branch: {repo["defaultBranch"]}')
        print('')
        print('List of Active Branches')
        paramBranch = {
            'columns' : [
                {'title' : 'Name'  , 'type': 'str',  'dataName': 'branchName'}
            ]
        }
        o7lib.util.displays.Table(paramBranch, branches)
        #pprint.pprint(branches)
        print('')

        print('Pull Requests')
        paramPr = {

            'columns' : [
                {'title' : 'id'      , 'type': 'i' },
                {'title' : 'Request Id'  , 'type': 'str',  'dataName': 'pullRequestId'},
                {'title' : 'Status'  , 'type': 'str',  'dataName': 'pullRequestStatus'},
                {'title' : 'Created', 'type': 'date', 'dataName': 'creationDate'},
                {'title' : 'Author', 'type': 'str', 'dataName': 'author'},
                {'title' : 'source', 'type': 'str', 'dataName': 'target.sourceReference'},

                {'title' : 'Title' , 'type': 'str', 'dataName': 'title'},
            ]
        }
        o7lib.util.displays.Table(paramPr, pullRequests)



    #*************************************************
    #
    #*************************************************
    def DisplayDifferences(self, differences):
        """Displays a summary Differemces"""
        print('')
        params = {
            'columns' : [
                {'title' : 'id'      , 'type': 'i'  },
                {'title' : 'T'    , 'type': 'str',  'dataName': 'changeType'},
                {'title' : 'File'    , 'type': 'str', 'dataName': 'path'},
                {'title' : 'Before'    , 'type': 'int', 'dataName': 'beforeBlob.lineCount'},
                {'title' : 'After'    , 'type': 'int', 'dataName': 'afterBlob.lineCount'},
            ]
        }
        o7lib.util.displays.Table(params, differences)


    #*************************************************
    #
    #*************************************************
    def MenuPullRequestDetails(self, pullRequestId):
        """Menu to view and edit a Pull Request"""



        while True :

            pullRequest = self.LoadPullRequests(pullRequestId=pullRequestId)[0]
            comments = self.LoadComments(pullRequestId=pullRequestId)
            self.DisplayPullRequestDetails(pullRequest=pullRequest, comments=comments)

            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Merge(m) Override Approval(o) Differences(d) Comment(int): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break

                if key.lower() == 'r':
                    pprint.pprint(pullRequest)
                    o7lib.util.input.WaitInput()

                if key.lower() == 'm':
                    self.MergePullRequest(pullRequestId)

                if key.lower() == 'o':
                    self.OverrideApproval(pullRequestId)

                if key.lower() == 'd':
                    differences = self.LoadDifferences(
                        repoName=pullRequest['target']['repositoryName'],
                        afterCommit=pullRequest['target']['sourceReference'],
                        beforeCommit=pullRequest['target']['mergeBase']
                    )
                    self.DisplayDifferences(differences)

                    o7lib.util.input.WaitInput()



            if keyType == 'int' and key > 0 and key <= len(comments):
                pprint.pprint(comments[key-1])
                o7lib.util.input.WaitInput()

    #*************************************************
    #
    #*************************************************
    def MenuRepoDetails(self, repoName):
        """Menu to view and edit details of a Repo"""



        while True :

            repo = self.LoadRepos(repoName=repoName)[0]
            branches = self.LoadBranches(repoName)
            pullRequests = self.LoadPullRequests(repoName=repoName)
            self.DisplayReposDetails(repo=repo, branches=branches, pullRequests=pullRequests)

            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) New Pull Request(p) Details(int): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break

                if key.lower() == 'r':
                    pprint.pprint(repo)
                    o7lib.util.input.WaitInput()

                if key.lower() == 'p':
                    self.CreatePullRequest(repoName, destination=repo["defaultBranch"])

            if keyType == 'int' and key > 0 and key <= len(pullRequests):
                # pprint.pprint(pullRequests[key-1])
                # o7lib.util.input.WaitInput()
                self.MenuPullRequestDetails(pullRequests[key-1]['pullRequestId'])


    #*************************************************
    #
    #*************************************************
    def MenuRepos(self):
        """Menu to view and edit all codecommit repos in current region"""

        while True :

            repos = self.LoadRepos()
            self.DisplayRepos(repos)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Details(int): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break

                if key.lower() == 'r':
                    pprint.pprint(repos)
                    o7lib.util.input.WaitInput()


            if keyType == 'int' and key > 0 and key <= len(repos):
                self.MenuRepoDetails(repos[key - 1].get('repositoryName'))

#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    CodeCommit().MenuRepos()

    # theComments = CodeCommit().LoadComments(pullRequestId='1061')
    # pprint.pprint(theComments)
