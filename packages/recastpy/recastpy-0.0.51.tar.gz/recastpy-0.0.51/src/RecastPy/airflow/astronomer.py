from RecastPy.aws.secrets_manager import get_secret_value
from json import loads, dumps
from datetime import datetime, timedelta
import urllib3
from RecastPy.misc import build_job_name_prefix, datetime_from_string

AIRFLOW_API_BASE_URL = 'https://deployments.gcp0001.us-east4.astronomer.io/weightless-wavelength-0417/airflow/api/v1/'


def _get_airflow_api_key():
    # get the Airflow API key from a secret
    api_key = get_secret_value('prod/astro/workspace/api_key/recast_programmatic', 'api_key')
    return api_key


def _make_airflow_api_request(method, endpoint, fields=None):
    http = urllib3.PoolManager()

    url = f"{AIRFLOW_API_BASE_URL}{endpoint}"
    api_key = _get_airflow_api_key()

    response = http.request(
        method=method,
        url=url,
        headers={
            'Authorization': api_key,
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        fields=fields
    )

    return loads(response.data.decode('utf-8'))


def get_dag_runs(dag_id, include_inactive=False, maximum_days_old=None, execution_date=None):
    if maximum_days_old and execution_date:
        raise Exception('Either the minimum_days_old or execution_date parameter can be specified, but not both.')

    if maximum_days_old:
        min_execution_date = datetime.now() - timedelta(days=maximum_days_old)
        fields = {
            'execution_date_gte': min_execution_date.strftime("%Y-%m-%dT%H:%M:%S"),
            'limit': 100,
            'offset': 0
        }
    else:
        fields = None

    if execution_date:
        if isinstance(execution_date, str):
            execution_date = datetime_from_string(execution_date)

        fields = {
            'execution_date_lte': (execution_date + timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%S"),
            'execution_date_gte': execution_date.strftime("%Y-%m-%dT%H:%M:%S"),
            'limit': 100,
            'offset': 0
        }

    runs = []
    while True:
        response = _make_airflow_api_request(method='GET', endpoint=f"dags/{dag_id}/dagRuns", fields=fields)

        # build the expected return response from the Airflow API response
        dag_runs = response.get('dag_runs', [])
        for run in dag_runs:
            state = run['state']
            if (not include_inactive) and (state in ['success', 'failed']):
                continue

            runs.append(run)

        if len(dag_runs) == 100:
            # get the next 100 dag runs
            fields['offset'] += 100
        else:
            # we've got all the dag runs, so exit the loop
            break

    return runs


def get_dag_run(dag_id, run_id):
    response = _make_airflow_api_request(method='GET', endpoint=f"dags/{dag_id}/dagRuns/{run_id}")

    return response


if __name__ == '__main__':
    # print(dumps(get_dag_runs(), indent=4))
    # print(dumps(get_dag_run(run_id='manual__2022-02-22T20:29:54.661414+00:00'), indent=4))
    dag_id = 'run_all_fleets'
    # run_id = 'manual__2022-02-22T20:29:54.661414+00:00'
    # run = get_dag_run(dag_id=dag_id, run_id=run_id)
    # name = build_job_name_prefix(dag_id='run_all_fleets', execution_date=run['execution_date'], fleet_id="fleet")
    # print(get_dag_runs(dag_id=dag_id))
    # print(get_dag_runs(dag_id=dag_id, include_inactive=True, execution_date='2022-02-23T17:25:44.645872+00:00'))
    print(get_dag_runs(dag_id=dag_id, include_inactive=True, maximum_days_old=7))

    pass
