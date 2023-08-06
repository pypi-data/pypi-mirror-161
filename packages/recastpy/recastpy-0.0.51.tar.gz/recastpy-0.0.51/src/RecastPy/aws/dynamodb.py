from boto3 import resource
from json import loads, dumps
from decimal import Decimal

__REGION__ = 'us-east-1'


def set_region(region):
    global __REGION__

    __REGION__ = region


def get_item(table: str, key: dict, region=__REGION__):
    def _decimal_to_int(obj):
        if isinstance(obj, Decimal):
            return int(obj)

    # Get a reference to the dynamodb table.
    dynamodb = resource(
        'dynamodb',
        region_name=region
    )

    # Fetch the record from the table and return it to the caller.
    response = dynamodb.Table(table).get_item(Key=key)
    item = response.get('Item', None)
    if item:
        item = loads(dumps(item, default=_decimal_to_int))

    return item


def put_item(table: str, item: dict, region=__REGION__):
    # Get a reference to the dynamodb table.
    dynamodb = resource(
        'dynamodb',
        region_name=region
    )

    # Write the record from the table.
    dynamodb.Table(table).put_item(Item=item)


if __name__ == '__main__':
    import time

    # item = {
    #     'DagRunId': 'test',
    #     'status_detail': {'some_string': 'some_value', 'some_number': 1},
    #     'ttl': int(time.time()) + (60 * 60 * 24)  # 24 hours from now
    # }
    # put_item(table='airflow-ingest_client_data-sensor', item=item)

    item = get_item(table='airflow-ingest_client_data-sensor', key={'DagRunId': 'test'})
    print(item)
