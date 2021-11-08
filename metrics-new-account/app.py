from __future__ import print_function
import json
import boto3
import logging
import jsonpickle

print('Loading function')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    for record in event['Records']:
        message = record['Sns']['Message']
        print("From SNS: " + message)
        logger.info('## EVENT\r' + jsonpickle.encode(event))
        logger.info('## CONTEXT\r' + jsonpickle.encode(context))
        logger.info('## MESSAGE\r' + jsonpickle.encode(message))
        # return response['AccountUsage']
        run_automation_metrics(message)
        return message
    return ""


def run_automation_metrics(payload):
    for account in payload['accounts']:
        account_id = account['account_id']
        account_name = account['account_name']
        region = account['region']
        environment = account['environment'].lower()
        metrics_url_thanos = f'metrics.${environment}.aws.cloud.ihf'
        bucket_name = f'cloudmetrics-thanos-${account_id}-metrics'

        create_bucket(bucket_name)
        add_ssm_parameter('/Observability/Account/Information/AccountID', account_id)
        add_ssm_parameter('/Observability/Account/Information/AccountName', account_name)
        add_ssm_parameter('/Observability/Account/Information/Region', region)
        add_ssm_parameter('/Observability/Account/Information/Environment', environment)
        add_ssm_parameter('/Observability/Metrics/MetricsURL', metrics_url_thanos)


def create_bucket(bucket_name):
    '''
    :param bucket_name: The name of bucket for creation
    :return:
    '''
    try:
        s3 = boto3.client('s3')
        response = s3.create_bucket(
            Bucket=bucket_name,
            GrantFullControl='string',
            GrantRead='string',
            GrantReadACP='string',
            GrantWrite='string',
            GrantWriteACP='string',
            ObjectLockEnabledForBucket=True | False
        )
        return response
    except:
        print("Error")
        return


def add_ssm_parameter(key, value, parameter_type='String', data_type='text'):
    '''
    :param key: Name of SSM Parameter (FQN) to be stored
    :param value: Value of SSM Parameter to be stored
    :param parameter_type: 'String'|'StringList'|'SecureString',
    :param data_type: 'text'|'aws:ec2:image'
    :return:
    Other Params that can be passed to SSM_PUT_PARAM
    # Tier='Standard'|'Advanced'|'Intelligent-Tiering',
    '''
    ssm = boto3.client('ssm')
    response = ssm.put_parameter(
        Name=key,
        Description='Parametro adicionado pela comunidade de confiabilidade para uso das ferramentas de observabilidade',
        Value=value,
        Type=parameter_type,
        Overwrite=True,
        Tags=[
            {
                'Key': 'string',
                'Value': 'string'
            },
        ],
        Policies='string',
        DataType=data_type
    )
    return response
