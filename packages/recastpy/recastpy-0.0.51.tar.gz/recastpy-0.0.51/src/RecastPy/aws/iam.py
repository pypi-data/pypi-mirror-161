from boto3 import client

__REGION__ = 'us-east-1'


def set_region(region):
    global __REGION__

    __REGION__ = region


def get_user_tags(username: str, region=__REGION__):
    iam = client(
        'iam',
        region_name=region
    )

    try:
        user = iam.get_user(UserName=username)
        return user.get('User', {}).get('Tags')
    except iam.exceptions.NoSuchEntityException as e:
        return None


def get_user_tag(username: str, tag: str, region=__REGION__):
    tags = get_user_tags(
        username=username,
        region=region
    ) or {}

    matching_tags = [t['Value'] for t in tags if t['Key'] == tag]

    # There are either no matches, or only one...
    if matching_tags:
        return matching_tags[0]
    else:
        return None


if __name__ == '__main__':
    tags = get_user_tag('jeff_carey', 'slack_id')
    print(tags)
