import json
from RecastPy.aws.secrets_manager import get_secret
from RecastPy.aws.iam import get_user_tag
from slack_sdk import WebClient

__REGION__ = 'us-east-1'
__TOKEN__ = None


def set_region(region):
    global __REGION__

    __REGION__ = region


def set_token(token=None):
    global __TOKEN__, __REGION__

    if token:
        __TOKEN__ = token
    else:
        __TOKEN__ = get_secret(
            secret_name='prod/slack/token/recast-alert-bot',
            region=__REGION__
        )


def get_token():
    global __TOKEN__, __REGION__

    if __TOKEN__:
        return __TOKEN__
    else:
        return get_secret(
            secret_name='prod/slack/token/recast-alert-bot',
            region=__REGION__
        )


def post_message(channel: str, message: str = None, blocks: list = None, icon_emoji: str = None):
    slack = WebClient(token=get_token())

    slack.chat_postMessage(
        channel=channel,
        text=message,
        blocks=json.dumps(blocks),
        icon_emoji=icon_emoji
    )


def create_message_block(block_type, block_text=None, fields=None, icon=None, double_icon=None, aws_username=None,
                         url=None):

    if block_type not in ['header', 'attention', 'text', 'button', 'divider', 'fields']:
        raise Exception(f'Unknown block_type: {block_type}')
    
    if block_type == 'header':
        block = {
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': f'{icon if icon else double_icon if double_icon else ""} {block_text} {double_icon if double_icon else ""}'.strip(),
                'emoji': True if icon or double_icon else False
            }
        }
    elif block_type == 'divider':
        block = {
                "type": "divider"
        }
    elif block_type == 'attention':
        slack_user_id = '<!channel>'

        if aws_username:
            user_tag = get_user_tag(username=aws_username, tag='slack_id')

            if user_tag:
                slack_user_id = f'<@{user_tag}>'

        block = {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*:point_right: Attention: {slack_user_id}*'
            }
        }
    elif block_type == 'text':
        block = {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': block_text
            }
        }
    elif block_type == 'fields':
        fields_list = []
        for field in fields:
            fields_list.append({"type": "mrkdwn", "text": field})

        block = {
            "type": "section",
            "fields": fields_list
        }
    elif block_type == 'button':
        block = {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": block_text
                    },
                    "style": "primary",
                    "url": url
                }
            ]
        }

    return block


if __name__ == '__main__':
    # for testing
    blocks = [
        create_message_block('header', block_text='Run Failure', double_icon=':rotating_light:'),
        create_message_block('attention', aws_username='jeff_carey'),
        create_message_block('text', 'There seems to be a problem...'),
        create_message_block('divider'),
        create_message_block('text', 'Here are the details...\n(See list below)\n\nMaybe Google can help?'),
        create_message_block('fields', fields=['field1', 'field2', 'field3']),
        create_message_block('button', block_text='Google', url='http://www.google.com')
    ]

    post_message(channel='slack-test', blocks=blocks, icon_emoji=":robot_face:")
