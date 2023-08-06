#!/usr/bin/env python
#************************************************************************
# Copyright 2022 O7 Conseils inc (Philippe Gosselin)
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
"""Module allows to view and access ECS Cluster, Services & Task"""


# How to bash into container
# https://aws.amazon.com/blogs/containers/new-using-amazon-ecs-exec-access-your-containers-fargate-ec2/
# aws ecs --profile cw execute-command  `
#     --cluster dev-nlsb-service-ecs-cluster `
#     --region ca-central-1 `
#     --task 7f467e5b42d34d4cbfec6f6bb6a7b389 `
#     --container nlsb `
#     --command "/bin/bash" `
#     --interactive
# See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html#ECS.Client.execute_command

#--------------------------------
#
#--------------------------------
import pprint
import logging
import subprocess

import o7lib.util.input
import o7lib.util.displays
import o7lib.aws.base


logger=logging.getLogger(__name__)

#*************************************************
#
#*************************************************
class Ecs(o7lib.aws.base.Base):
    """Class for ECS for a Profile & Region"""

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html#client

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None):
        super().__init__(profile=profile, region=region)
        self.ecs = self.session.client('ecs')



    #*************************************************
    #
    #*************************************************
    def LoadClusters(self, cluster = None):
        """Returns all Clusters """

        logger.info('LoadClusters')

        clusters = []
        param={}


        done=False
        while not done:

            clustersRequest = []

            if cluster is None:
                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html#ECS.Client.list_clusters
                resp = self.ecs.list_clusters(**param)
                #pprint.pprint(resp)
                logger.info(f'LoadClusters: Number of Clusters {len(resp["clusterArns"])}')

                if 'nextToken' in resp:
                    param['nextToken'] = resp['nextToken']
                else:
                    done = True

                if len(resp["clusterArns"]) == 0:
                    return clusters

                clustersRequest = resp["clusterArns"]
            else:
                done = True
                clustersRequest.append(cluster)


            respDetails = self.ecs.describe_clusters(clusters=clustersRequest)
            # pprint.pprint(respDetails)
            clusters += respDetails["clusters"]

        return clusters


    #*************************************************
    #
    #*************************************************
    def LoadServices(self, cluster : str):
        """Returns all Clusters """

        logger.info(f'LoadServices for cluster : {cluster}')

        services = []
        param={
            'cluster' : cluster
        }

        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html#ECS.Client.list_clusters
            resp = self.ecs.list_services(**param)
            #pprint.pprint(resp)
            logger.info(f'LoadServices: Number of Services {len(resp["serviceArns"])}')

            if 'nextToken' in resp:
                param['nextToken'] = resp['nextToken']
            else:
                done = True

            if len(resp["serviceArns"]) == 0:
                return services

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html#ECS.Client.describe_services
            respDetails = self.ecs.describe_services(cluster = cluster, services=resp["serviceArns"])
            # pprint.pprint(respDetails)
            services += respDetails["services"]

        return services


    #*************************************************
    #
    #*************************************************
    def LoadInstances(self, cluster : str):
        """Returns all Clusters """

        logger.info(f'LoadInstances for cluster : {cluster}')

        instances = []
        param={
            'cluster' : cluster
        }

        done=False
        while not done:

            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html#ECS.Client.list_container_instances
            resp = self.ecs.list_container_instances(**param)
            #pprint.pprint(resp)
            logger.info(f'LoadInstances: Number of Instances {len(resp["containerInstanceArns"])}')

            if 'nextToken' in resp:
                param['nextToken'] = resp['nextToken']
            else:
                done = True

            if len(resp["containerInstanceArns"]) == 0:
                return instances

            respDetails = self.ecs.describe_container_instances(cluster = cluster, containerInstances=resp["containerInstanceArns"])
            # pprint.pprint(respDetails)
            instances += respDetails["containerInstances"]

        return instances

    #*************************************************
    #
    #*************************************************
    def LoadTasks(self, cluster : str, service: str = None, taskId: str = None):
        """Returns all Tasks """

        logger.info(f'LoadTasks for cluster={cluster}  service={service}')

        tasks = []
        param={
            'cluster' : cluster,
        }

        if service is not None:
            param['service'] = service


        done=False
        while not done:

            taskRequest = []

            if taskId is None:
                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecs.html#ECS.Client.list_tasks
                resp = self.ecs.list_tasks(**param)
                #pprint.pprint(resp)
                logger.info(f'LoadServices: Number of Tasks {len(resp["taskArns"])}')

                if 'nextToken' in resp:
                    param['nextToken'] = resp['nextToken']
                else:
                    done = True

                if len(resp["taskArns"]) == 0:
                    break

                taskRequest = resp["taskArns"]

            else:
                done = True
                taskRequest.append(taskId)

            respDetails = self.ecs.describe_tasks(cluster = cluster, tasks=taskRequest)
            # pprint.pprint(respDetails)
            tasks += respDetails["tasks"]

        for task in tasks:
            task['taskId'] = task.get('taskArn',"").split('/')[-1]


        return tasks


    #*************************************************
    #
    #*************************************************
    def DisplayClusters(self, clusters):
        """Diplay Instances"""
        self.ConsoleTitle(left='ECS Clusters')
        print('')
        params = {
            'columns' : [
                {'title' : 'id',          'type': 'i',    'minWidth' : 4  },
                {'title' : 'Cluster Name',     'type': 'str',  'dataName': 'clusterName'},
                {'title' : 'Status', 'type': 'str',  'dataName': 'status', 'format' : 'aws-status'},
                {'title' : 'Running Task', 'type': 'int', 'dataName': 'runningTasksCount'},
                {'title' : 'Pending Task', 'type': 'int', 'dataName': 'pendingTasksCount'},

                {'title' : 'Services', 'type': 'int', 'dataName': 'activeServicesCount'},
                {'title' : 'Instances', 'type': 'int', 'dataName': 'registeredContainerInstancesCount'},

            ]
        }
        o7lib.util.displays.Table(params, clusters)

    #*************************************************
    #
    #*************************************************
    def DisplayCluster(self, clusterDetails, services, instances, tasks):
        """Diplay Instances"""
        self.ConsoleTitle(left=f'ECS Clusters for {clusterDetails["clusterName"]}')
        print('')

        print(f'Status: {clusterDetails["status"]}')
        print(f'Pending Tasks: {clusterDetails["pendingTasksCount"]}')

        params = {
            'columns' : [
                {'title' : 'Service Name',     'type': 'str',  'dataName': 'serviceName'},
                {'title' : 'Status', 'type': 'str',  'dataName': 'status', 'format' : 'aws-status'},

                {'title' : 'Desired', 'type': 'int', 'dataName': 'desiredCount'},
                {'title' : 'Running', 'type': 'int', 'dataName': 'runningCount'},
                {'title' : 'Pending', 'type': 'int', 'dataName': 'pendingCount'},

                {'title' : 'Type', 'type': 'str', 'dataName': 'launchType'},


            ]
        }
        print('')
        print('List of Services')
        o7lib.util.displays.Table(params, services)

        params = {
            'columns' : [
                {'title' : 'Instance Id',     'type': 'str',  'dataName': 'ec2InstanceId'},
                {'title' : 'Status', 'type': 'str',  'dataName': 'status', 'format' : 'aws-status'},

                {'title' : 'Running', 'type': 'int', 'dataName': 'runningTasksCount'},
                {'title' : 'Pending', 'type': 'int', 'dataName': 'pendingTasksCount'}
            ]
        }
        print('')
        print('List of Instances')
        o7lib.util.displays.Table(params, instances)


        params = {
            'columns' : [
                {'title' : 'id',          'type': 'i',    'minWidth' : 4  },
                {'title' : 'Task Name',     'type': 'str',  'dataName': 'taskId'},
                {'title' : 'Status', 'type': 'str',  'dataName': 'lastStatus', 'format' : 'aws-status'},
                {'title' : 'Health', 'type': 'str',  'dataName': 'healthStatus', 'format' : 'aws-status'},


                {'title' : 'CPU', 'type': 'int', 'dataName': 'cpu'},
                {'title' : 'Memory', 'type': 'int', 'dataName': 'memory'},
                {'title' : 'Stated', 'type': 'datetime', 'dataName': 'startedAt'},

                {'title' : 'Type', 'type': 'str', 'dataName': 'launchType'},
                {'title' : 'Zone', 'type': 'str', 'dataName': 'availabilityZone'},
                {'title' : 'ECS Exec', 'type': 'str', 'dataName': 'enableExecuteCommand'},



            ]
        }
        print('')
        print('List of Tasks')
        o7lib.util.displays.Table(params, tasks)



    #*************************************************
    #
    #*************************************************
    def DisplayTask(self, taskDetails):
        """Diplay Instances"""
        self.ConsoleTitle(left=f'ECS Task Details for: {taskDetails["taskId"]}')
        print('')
        print(f'Status: {taskDetails["lastStatus"]}')
        print(f'Health: {taskDetails["healthStatus"]}')
        print(f'Started At: {taskDetails["startedAt"]}')

        print('')
        print(f'Launch Type: {taskDetails["launchType"]}')
        print(f'CPU: {taskDetails["cpu"]}')
        print(f'Memory: {taskDetails["memory"]}')

        print('')
        print(f'Availability Zone: {taskDetails["availabilityZone"]}')
        print(f'Exec Command Enabled: {taskDetails["enableExecuteCommand"]}')
        print(f'Group: {taskDetails["group"]}')

        print('')

    #*************************************************
    #
    #*************************************************
    def CmdIn(self, taskDetails, cmd = '/bin/bash'):
        """Start a Shell inside a task contatiner"""

        cluster = taskDetails["clusterArn"].split('/')[-1]

        print('List of containers is task')
        containers = taskDetails.get('containers', [])
        for i, container in enumerate(containers):
            print(f'{i} -> {container["name"]}')

        key = o7lib.util.input.InputInt('Select container id : ')

        if key is None or  key < 0 or key >= len(containers):
            return

        procCmd = f'aws --profile {self.session.profile_name} --region {self.session.region_name} ecs execute-command '
        procCmd +=f'--cluster {cluster} --task {taskDetails["taskId"]} --container {containers[key]["name"]} '
        procCmd +=f'--command "{cmd}" --interactive'
        print(f'Command: {procCmd}')
        subprocess.call(procCmd, shell = True)



    #*************************************************
    #
    #*************************************************
    def MenuClusters(self):
        """View of all clusters"""

        while True :

            clusters = sorted(self.LoadClusters(), key=lambda x: x['clusterName'])
            self.DisplayClusters(clusters)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Details(int): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'r':
                    pprint.pprint(clusters)
                    o7lib.util.input.WaitInput()

            if keyType == 'int' and  0 < key <= len(clusters):
                self.MenuCluster(cluster=clusters[key - 1]['clusterName'])


    #*************************************************
    #
    #*************************************************
    def MenuCluster(self, cluster):
        """View details of a single cluster"""

        while True :

            clusterDetails = self.LoadClusters(cluster=cluster)[0]
            services = self.LoadServices(cluster=cluster)
            instances = self.LoadInstances(cluster=cluster)
            tasks = self.LoadTasks(cluster=cluster)

            self.DisplayCluster(clusterDetails, services=services, instances=instances, tasks=tasks)
            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Details(int): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'r':
                    pprint.pprint(clusterDetails)
                    o7lib.util.input.WaitInput()

            if keyType == 'int' and  0 < key <= len(tasks):
                self.MenuTask(cluster=cluster, taskId=tasks[key-1]['taskId'])



    #*************************************************
    #
    #*************************************************
    def MenuTask(self, cluster, taskId):
        """Task Detailed View"""

        while True :

            taskDetails = self.LoadTasks(cluster=cluster, taskId=taskId)[0]
            self.DisplayTask(taskDetails=taskDetails)

            keyType, key = o7lib.util.input.InputMulti('Option -> Back(b) Raw(r) Bash-In(a) Sh-In(s): ')

            if keyType == 'str':
                if key.lower() == 'b':
                    break
                if key.lower() == 'r':
                    pprint.pprint(taskDetails)
                    o7lib.util.input.WaitInput()

                if key.lower() == 'a':
                    self.CmdIn(taskDetails=taskDetails, cmd='/bin/bash')
                    o7lib.util.input.WaitInput()

                if key.lower() == 's':
                    self.CmdIn(taskDetails=taskDetails, cmd='/bin/sh')
                    o7lib.util.input.WaitInput()


#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    Ecs().MenuClusters()
