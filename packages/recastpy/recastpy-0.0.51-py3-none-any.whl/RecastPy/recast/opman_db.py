import psycopg2
import logging
import uuid
import json
from copy import copy
from datetime import datetime as dt
from RecastPy.aws import secrets_manager


########################################################################################################################
# Private functions
########################################################################################################################

def _get_connection():
    conn_string = secrets_manager.get_secret_value('prod/rds/opman_db', 'connection_string')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    try:
        conn = psycopg2.connect(conn_string)
    except Exception as e:
        logger.error("ERROR: Unexpected error: Could not connect to RDS database instance.")
        logger.error(e)
        raise e

    return conn


########################################################################################################################
# Batch event capture
########################################################################################################################

def create_batch_state_change_event(
        event_id: str,
        event_data: str,
        test: bool = False
):
    with _get_connection() as conn:
        with conn.cursor() as cur:
            sql = (
                f"SELECT public.batch_state_change_event_insert{'_test' if test else ''}(cast(%s as uuid), cast(%s as jsonb))"
            )
            cur.execute(sql, (event_id, event_data))
            conn.commit()


########################################################################################################################
# OpMan
########################################################################################################################

def create_fleet_run(
        client_name: str,
        aws_username: str,
        test_run: bool,
        git_sha: str,
        optimizer_git_sha: str,
        clients_git_sha: str,
        automated_launch: bool,
        s3_root_path: str,
        platform_config: str,
        legacy_job_id: str = None,
        legacy_dag_id: str = None,
        legacy_execution_date: str = None
):
    fleet_run_id = str(uuid.uuid4())

    with _get_connection() as conn:
        with conn.cursor() as cur:
            sql = (
                "INSERT INTO public.fleet_run "
                "(fleet_run_id, client_name, aws_username, test_run, git_sha, optimizer_git_sha, clients_git_sha, automated_launch, s3_root_path, platform_config, legacy_job_id, legacy_dag_id, legacy_execution_date) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            )
            cur.execute(sql, (fleet_run_id, client_name, aws_username, test_run, git_sha, optimizer_git_sha, clients_git_sha, automated_launch, s3_root_path, platform_config, legacy_job_id, legacy_dag_id, legacy_execution_date))
            conn.commit()

    return fleet_run_id


def create_model_run(
        fleet_run_id: str,
        s3_stacking_path: str,
        depvar_name: str,
        subset_name: str,
        model_count: int,
        platform_config: str,
        legacy_fleet_id: str = None,
        legacy_job_id: str = None
):
    model_run_id = str(uuid.uuid4())

    with _get_connection() as conn:
        with conn.cursor() as cur:
            sql = (
                "INSERT INTO public.model_run "
                "(model_run_id, fleet_run_id, s3_stacking_path, depvar_name, subset_name, model_count, platform_config, legacy_fleet_id, legacy_job_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
            )
            cur.execute(sql, (model_run_id, fleet_run_id, s3_stacking_path, depvar_name, subset_name, model_count, platform_config, legacy_fleet_id, legacy_job_id))
            conn.commit()

    return model_run_id


def create_model_run_task(
        model_run_id: str,
        job_id: str,
        job_name: str,
        task_type: str,
        legacy_fleet_id: str = None,
        grouping: str = None
):
    model_run_task_id = str(uuid.uuid4())

    with _get_connection() as conn:
        with conn.cursor() as cur:
            sql = (
                "INSERT INTO public.model_run_task "
                "(model_run_task_id, model_run_id, job_id, task_type, legacy_fleet_id, grouping) "
                "VALUES (%s, %s, %s, %s, %s, %s) "
            )
            cur.execute(sql, (model_run_task_id, model_run_id, job_id, task_type, legacy_fleet_id, grouping))

            sql = (
                "INSERT INTO public.batch_job "
                "(job_id, job_name) "
                "VALUES (%s, %s) "
                "ON CONFLICT (job_id) DO "
                "UPDATE SET "
                "   job_name = %s "
            )
            cur.execute(sql, (job_id, job_name, job_id))

            conn.commit()

    return model_run_task_id


def read_fleet_runs(max_days_old: int = 7):
    with _get_connection() as conn:
        with conn.cursor() as cur:
            sql = "select * from public.fleet_run_select(%s);"
            cur.execute(sql, (str(max_days_old)))

            records = cur.fetchall()

    fleets = []
    fleet = {desc[0]: None for desc in cur.description}
    column_names = [desc[0] for desc in cur.description]

    for row in records:
        f = copy(fleet)

        for idx, nm in enumerate(column_names):
            key = nm
            if isinstance(row[idx], dt):
                val = row[idx].strftime('%Y-%m-%d %H:%M:%S')
            else:
                val = row[idx]

            f[key] = val

        fleets.append(f)

    return fleets


def read_model_runs(fleet_run_id: uuid = None, legacy_job_id: str = None, max_days_old: int = 7):
    if fleet_run_id is None and legacy_job_id is None:
        raise Exception("You must provide a value for either fleet_run_id or legacy_job_id.")

    with _get_connection() as conn:
        with conn.cursor() as cur:
            sql = "select * from public.model_run_select(null, %s, null, %s, 'model_run', %s);"
            cur.execute(sql, (fleet_run_id, legacy_job_id, str(max_days_old)))

            records = cur.fetchall()

    model_runs = []
    model_run = {desc[0]: None for desc in cur.description}
    column_names = [desc[0] for desc in cur.description]

    for row in records:
        f = copy(model_run)

        for idx, nm in enumerate(column_names):
            key = nm
            if isinstance(row[idx], dt):
                val = row[idx].strftime('%Y-%m-%d %H:%M:%S')
            else:
                val = row[idx]

            f[key] = val

        model_runs.append(f)

    return model_runs


def read_model_run_tasks(model_run_id: str = None, legacy_fleet_id: str = None, max_days_old: int = 7):
    if model_run_id is None and legacy_fleet_id is None:
        raise Exception("You must provide a value for either model_run_id or legacy_fleet_id.")

    with _get_connection() as conn:
        with conn.cursor() as cur:
            sql = "select * from public.model_run_task_select(%s, null, %s, null, %s);"
            cur.execute(sql, (model_run_id, legacy_fleet_id, str(max_days_old)))

            records = cur.fetchall()

    model_run_tasks = []
    model_run_task = {desc[0]: None for desc in cur.description}
    column_names = [desc[0] for desc in cur.description]

    for row in records:
        f = copy(model_run_task)

        for idx, nm in enumerate(column_names):
            key = nm
            if isinstance(row[idx], dt):
                val = row[idx].strftime('%Y-%m-%d %H:%M:%S')
            else:
                val = row[idx]

            f[key] = val

        model_run_tasks.append(f)

    return model_run_tasks


# def create_data_ingest_task(ingest_id, task_type, job_id, *kwargs):
#     if task_type == 'clean_and_store':
#         required_kwargs = ['client_name', 'aws_username', 'script']
#     else:
#         raise Exception(f'Unknown task_type: {task_type}')
#
#     if required_kwargs not in kwargs:
#         raise Exception(f'Missing kwargs: {list(set(kwargs) - set(required_kwargs))}')
#
#     with _get_connection() as conn:
#         with conn.cursor() as cur:
#             sql = """
#                 insert into data_ingest
#                 (ingest_id, )
#             """
#             cur.execute()
#             cur.commit()


########################################################################################################################
# Debugging
########################################################################################################################

if __name__ == '__main__':
    which_test = 1

    if which_test == 1:
        fleet_run_id = create_fleet_run(
            'demo',
            'jeff_carey',
            True,
            'master',
            'master',
            'master',
            False,
            's3://...',
            '{}',
            'run_all_fleets__20220625_191157',
            'run_all_fleets',
            '20220625_191157'
        )

        print(fleet_run_id)

        model_run_id = create_model_run(
            fleet_run_id,
            's3://...',
            'depvar',
            'subset',
            24,
            '{}',
            'recast-aphrodite_cc_conversions_20220625_150830_master_775a2ce8',
            'run_all_fleets__20220625_191157'
        )

        print(model_run_id)

        model_run_task_id = create_model_run_task(
            model_run_id,
            str(uuid.uuid4()),
            'test_job',
            'model_run',
            'recast-aphrodite_cc_conversions_20220625_150830_master_775a2ce8'
        )

        print(model_run_task_id)
    elif which_test == 2:
        start_time = dt.now()

        # ret_val = read_fleet_runs(1)
        # ret_val = read_model_runs(legacy_job_id='run_all_fleets__20220712_212545', max_days_old=1)
        ret_val = read_model_run_tasks(legacy_fleet_id='recast-ersa_dtc_est_ltv_20220712_170331_master_a4d7864a', max_days_old=1)

        end_time = dt.now()
        record_count = len(ret_val)

        print(json.dumps(ret_val, indent=4))
        print(f'total time: {end_time - start_time}')
        print(f'record count: {record_count}')
    elif which_test == 3:
        event_id = str(uuid.uuid4())
        print(event_id)
        event_data = json.dumps({"id": event_id, "time": "2022-06-18T09:10:08Z", "detail": {"tags": {"resourceArn": "arn:aws:batch:us-east-1:363039686001:job/740ee3ee-f235-4670-b19f-84da1bda6e76"}, "jobId": "740ee3ee-f235-4670-b19f-84da1bda6e76:12", "jobArn": "arn:aws:batch:us-east-1:363039686001:job/740ee3ee-f235-4670-b19f-84da1bda6e76:12", "status": "SUCCEEDED", "jobName": "run_all_fleets__20220618_030716__recast-dionysus_intro_orders_acquisitions_20220618_030240_channel-_4666200b__model_run", "attempts": [{"container": {"taskArn": "arn:aws:ecs:us-east-1:363039686001:task/AWSBatch-core_arm64_model_run_best_fit_20220420105141263200000008-f8d10bee-1f43-325d-b37c-9f4728eb7f8c/770a2f9cd4bb407c84227223b775ca25", "exitCode": 0, "logStreamName": "core_arm64_model_run/default/770a2f9cd4bb407c84227223b775ca25", "networkInterfaces": [], "containerInstanceArn": "arn:aws:ecs:us-east-1:363039686001:container-instance/AWSBatch-core_arm64_model_run_best_fit_20220420105141263200000008-f8d10bee-1f43-325d-b37c-9f4728eb7f8c/f2c1ca859f1849dc9ce4fece48ad2dfb"}, "startedAt": 1655521805856, "stoppedAt": 1655543406856, "statusReason": "Essential container in task exited"}], "jobQueue": "arn:aws:batch:us-east-1:363039686001:job-queue/core_arm64_model_run_standard", "container": {"image": "363039686001.dkr.ecr.us-east-1.amazonaws.com/recast_core:arm64", "command": ["/opt/utils/run_model.sh"], "secrets": [{"name": "AWS_ACCESS_KEY_ID", "valueFrom": "arn:aws:secretsmanager:us-east-1:363039686001:secret:prod/iam/airflow_user-Ccn6Oo:AWS_ACCESS_KEY_ID::"}, {"name": "AWS_SECRET_ACCESS_KEY", "valueFrom": "arn:aws:secretsmanager:us-east-1:363039686001:secret:prod/iam/airflow_user-Ccn6Oo:AWS_SECRET_ACCESS_KEY::"}, {"name": "AIRFLOW_API", "valueFrom": "arn:aws:secretsmanager:us-east-1:363039686001:secret:prod/astro/workspace/api_key/recast_programmatic-PkoWO5:api_key::"}, {"name": "GITHUB_TOKEN", "valueFrom": "arn:aws:secretsmanager:us-east-1:363039686001:secret:prod/github/token-R09kfb:github_token::"}, {"name": "GITHUB_PAT", "valueFrom": "arn:aws:secretsmanager:us-east-1:363039686001:secret:prod/github/token-R09kfb:github_token::"}], "taskArn": "arn:aws:ecs:us-east-1:363039686001:task/AWSBatch-core_arm64_model_run_best_fit_20220420105141263200000008-f8d10bee-1f43-325d-b37c-9f4728eb7f8c/770a2f9cd4bb407c84227223b775ca25", "ulimits": [], "volumes": [], "exitCode": 0, "environment": [{"name": "OPTIMIZER_GIT_SHA", "value": "develop"}, {"name": "RUN_TYPE", "value": "model_run"}, {"name": "TEST_RUN", "value": "False"}, {"name": "S3_STACKING_CONFIG_PATH", "value": "s3://recast-dionysus/recast/run-output/ALL/dionysus_channel_dependent_lf/feature/channel-dependent-lower-funnel/2022-06-18-03:02:40/intro_orders_acquisitions/stacked/AFKPL3362L"}, {"name": "S3_ROOT_PATH", "value": "s3://recast-dionysus/recast/run-output/ALL/dionysus_channel_dependent_lf/feature/channel-dependent-lower-funnel/2022-06-18-03:02:40"}, {"name": "DEPVAR_NAME", "value": "intro_orders_acquisitions"}, {"name": "GIT_SHA", "value": "4666200b077e644945eee66a4aafce8954eeabc6"}, {"name": "SUBSET_NAME", "value": "ALL"}, {"name": "CLIENT", "value": "dionysus"}], "mountPoints": [], "logStreamName": "core_arm64_model_run/default/770a2f9cd4bb407c84227223b775ca25", "linuxParameters": {"tmpfs": [], "devices": []}, "executionRoleArn": "arn:aws:iam::363039686001:role/core_ecsTaskExecutionRole", "networkInterfaces": [], "containerInstanceArn": "arn:aws:ecs:us-east-1:363039686001:container-instance/AWSBatch-core_arm64_model_run_best_fit_20220420105141263200000008-f8d10bee-1f43-325d-b37c-9f4728eb7f8c/f2c1ca859f1849dc9ce4fece48ad2dfb", "resourceRequirements": [{"type": "VCPU", "value": "2"}, {"type": "MEMORY", "value": "24576"}]}, "createdAt": 1655521641954, "dependsOn": [], "startedAt": 1655521805856, "stoppedAt": 1655543406856, "parameters": {}, "eksAttempts": [], "statusReason": "Essential container in task exited", "jobDefinition": "arn:aws:batch:us-east-1:363039686001:job-definition/core_arm64_model_run:5", "propagateTags": True, "retryStrategy": {"attempts": 2, "evaluateOnExit": []}, "arrayProperties": {"index": 12, "statusSummary": {}}, "platformCapabilities": ["EC2"]}, "region": "us-east-1", "source": "aws.batch", "account": "363039686001", "version": "0", "resources": ["arn:aws:batch:us-east-1:363039686001:job/740ee3ee-f235-4670-b19f-84da1bda6e76:12"], "detail-type": "Batch Job State Change"})
        create_batch_state_change_event(event_id=event_id, event_data=event_data)
    else:
        print("Which test do you want to run?")
