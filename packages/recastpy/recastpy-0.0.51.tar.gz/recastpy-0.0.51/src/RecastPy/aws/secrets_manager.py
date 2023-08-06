from boto3 import client
from json import loads
import logging

__REGION__ = 'us-east-1'


def set_region(region):
    global __REGION__

    __REGION__ = region


def get_secret(secret_name, region=__REGION__):
    # This function gets the value of a secret, i.e. the entire secret value.
    ssm = client(
        'secretsmanager',
        region_name=region
    )
    secret_string = ssm.get_secret_value(SecretId=secret_name)['SecretString']
    return secret_string


def get_secret_value(secret_name, secret_key, region=__REGION__):
    # This function gets a value from a specific key-value pair within a secret stored as a valid json string.
    ssm = client(
        'secretsmanager',
        region_name=region
    )
    secret_string = loads(ssm.get_secret_value(SecretId=secret_name)['SecretString'])
    return secret_string.get(secret_key, None)


def create_credentials_file_from_secrets(
        creds_filename: str,
        append: bool = False,
        aws_access_key_id=None,
        aws_secret_access_key=None
):
    """
    This function reads secrets from AWS, looking for all secrets with an "aws_profile" tag, and then uses those
    secrets to create a standard AWS credentials file, with a profile for each secret. The name of each profile will
    be the value of the aws_profile tag. It will OVERWRITE any existing file with the specified filename, unless
    append=True is specified. Each secret value is expected to have the following format:

    {
        "AWS_ACCESS_KEY_ID": "<key id>",
        "AWS_SECRET_ACCESS_KEY": "<secret key>"
    }

    :param creds_filename: A filename (with path) to write to. Will be OVERWRITTEN if it exists, unless append=True
        is specified.
    :param append: Append to creds_filename if True, otherwise overwrite. Defaults to False/overwrite.
    :param aws_access_key_id: Optionally specify the AWS creds this function will use to access secrets.
    :param aws_secret_access_key: Optionally specify the AWS creds this function will use to access secrets.

    :return None:
    """
    # get secretsmanager client
    sm = client(
        "secretsmanager",
        region_name="us-east-1",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    # get secrets with a tag with the key of "aws_profile"
    secrets = sm.list_secrets(
        Filters=[{"Key": "tag-key", "Values": ["aws_profile"]}]
    )

    # create a credentials file that we'll write the access keys to
    with open(creds_filename, mode='a' if append else 'w') as creds_file:
        # loop through all matching secrets
        for secret in secrets['SecretList']:
            # get the value of the aws_profile tag
            profile_name = [i['Value'] for i in secret['Tags'] if i['Key'] == 'aws_profile'][0]

            # get the access key from the secret
            try:
                secret_value = sm.get_secret_value(SecretId=secret['ARN'])
            except:
                # if access to this secret isn't permitted by the current credentials, warn but continue with the next
                # secret
                logging.warning(f'Unable to retrieve secret "{secret["Name"]}", no credentials profile created for '
                                f'that secret.')
                continue

            secret_string = loads(secret_value['SecretString'])
            aws_access_key_id = secret_string['AWS_ACCESS_KEY_ID']
            aws_secret_access_key = secret_string['AWS_SECRET_ACCESS_KEY']

            # write a profile to the credentials file
            creds_file.write(f'[{profile_name}]\n')
            creds_file.write(f'AWS_ACCESS_KEY_ID={aws_access_key_id}\n')
            creds_file.write(f'AWS_SECRET_ACCESS_KEY={aws_secret_access_key}\n\n')


def create_google_auth_token_file(
        creds_filename: str,
        aws_access_key_id=None,
        aws_secret_access_key=None
):
    # get secretsmanager client
    sm = client(
        "secretsmanager",
        region_name="us-east-1",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    # get secrets with a "google_auth" tag
    secrets = sm.list_secrets(
        Filters=[{"Key": "tag-key", "Values": ["google_auth"]}]
    )
    secrets_list = secrets.get('SecretList', [])

    # find the one with a "google_auth" tag value of "recast"
    recast_secret = None
    match_count = 0
    for secret in secrets_list:
        # get the value of the google_auth tag
        profile_name = [i['Value'] for i in secret['Tags'] if i['Key'] == 'google_auth'][0]

        # if it's "recast", it's the one we're looking for
        if profile_name == 'recast':
            match_count += 1
            recast_secret = secret.copy()

    # we should have found exactly one matching secret
    if match_count != 1:
        raise Exception(f'Expected to find 1 secret with a "google_auth" tag with a value of "recast", but found {match_count} instead.')

    # create a credentials file that we'll write the token to
    with open(creds_filename, 'w') as creds_file:
        # get the token from the secret
        secret_value = sm.get_secret_value(SecretId=secret['ARN'])
        secret_string = loads(secret_value['SecretString'])
        auth_token = secret_string['token']

        # write the token to the file
        creds_file.write(auth_token)


if __name__ == '__main__':
    # for testing...

    # sv = get_secret('prod/astro/workspace/api_key/recast_programmatic')
    # print(sv)
    # sv = get_secret_value('prod/astro/workspace/api_key/recast_programmatic', 'api_key')
    # print(sv)

    # create_credentials_file_from_secrets(creds_filename="credentials")

    create_google_auth_token_file(creds_filename="google_auth.json")
