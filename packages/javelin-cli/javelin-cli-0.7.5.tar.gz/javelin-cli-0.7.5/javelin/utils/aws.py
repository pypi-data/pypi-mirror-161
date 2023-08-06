"""AWS
"""

import sys
import time

import boto3
import yaml

##
## PUBLIC
##

def start_pipeline_execution_and_wait(project_name, env):
    codepipeline = boto3.client('codepipeline')
    pipeline_name = _get_project_pipeline_name(project_name, env)

    if not pipeline_name:
        return True

    res = codepipeline.start_pipeline_execution(name=pipeline_name)

    if res['ResponseMetadata']['HTTPStatusCode'] != 200:
        print("javelin: couldn't start pipeline")
        sys.exit(2)

    pipeline_execution_id = res['pipelineExecutionId']

    while True:
        try:
            res = codepipeline.get_pipeline_execution(
                pipelineName=pipeline_name,
                pipelineExecutionId=pipeline_execution_id
            )

            status = res['pipelineExecution']['status']

            if status == 'InProgress':
                print("\033[A\033[A")
                print(f'({pipeline_execution_id}) In progress...')
            elif status == 'Succeeded':
                print(f'({pipeline_execution_id}) Succeeded.')
                return True
            else:
                print(f'({pipeline_execution_id}) Execution ended with status "{status}"')
                return False
        except codepipeline.exceptions.PipelineExecutionNotFoundException:
            print(f'({pipeline_execution_id}) Waiting...')

        time.sleep(10)

##
## PRIVATE
##

def _get_project_pipeline_name(project_name, env):
    with open('./config/projects.yml', 'r', encoding='utf-8') as stream:
        try:
            config = yaml.safe_load(stream)

            return config[project_name]['codepipeline_names'][env]
        except (KeyError, yaml.YAMLError):
            return None
