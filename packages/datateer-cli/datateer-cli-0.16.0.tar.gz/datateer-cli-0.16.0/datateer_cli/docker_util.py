import base64
import random
import string
import subprocess

import boto3

# import docker


REPOSITORY_LIFECYCLE_POLICY = """
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep only two images, expire all others",
            "selection": {
                "tagStatus": "any",
                "countType": "imageCountMoreThan",
                "countNumber": 2
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
"""


# def get_aws_client(role_arn, aws_region, service_name='ecr'):
# key, secret, token = get_aws_session(role_arn)
# client = boto3.client(service_name, aws_access_key_id=key,
#                       aws_secret_access_key=secret, aws_session_token=token, region_name=aws_region)
# return client


# def get_aws_session(role_arn):
#     """Creates an AWS session for the role_arn. Assumes the caller has permission to assume the role"""
#     sts_client = boto3.client('sts')
#     session_name = 'pipeline-deployment-' + \
#         ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
#     assumed_role_obj = sts_client.assume_role(
#         RoleArn=role_arn, RoleSessionName=session_name)
#     creds = assumed_role_obj['Credentials']
#     return creds['AccessKeyId'], creds['SecretAccessKey'], creds['SessionToken']


def registry_info():
    """Gets registry information for the client ECR registry. Returns tuple of the registry's username, password, and URL."""
    # ecr_client = get_aws_client(role_arn, aws_region, 'ecr')
    ecr_client = boto3.client("ecr")
    ecr_creds = ecr_client.get_authorization_token()["authorizationData"][0]
    ecr_username = "AWS"
    ecr_password = (
        base64.b64decode(ecr_creds["authorizationToken"])
        .replace(b"AWS:", b"")
        .decode("utf-8")
    )
    ecr_url = ecr_creds["proxyEndpoint"].lstrip("https://")
    return ecr_username, ecr_password, ecr_url


def docker_login():
    """Logs into the docker registry for the client ECR registry. Works even if no repositories have been created yet."""
    username, password, url = registry_info()

    # the python docker library doesn't save credentials locally, so unfortunately we call subprocess instead
    # docker_client = docker.from_env()
    # res = docker_client.login(
    #     username=username, password=password, registry=url)
    # return res
    subprocess.run(["docker", "login", "-u", username, "-p", password, url])


def ensure_repository_exists(repo_name):
    # client = get_aws_client(role_arn, aws_region, 'ecr')
    client = boto3.client("ecr")
    try:
        client.create_repository(repositoryName=repo_name)
        client.put_lifecycle_policy(
            repositoryName=repo_name, lifecyclePolicyText=REPOSITORY_LIFECYCLE_POLICY
        )
    except client.exceptions.RepositoryAlreadyExistsException:
        pass
