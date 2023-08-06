import boto3
import logging
from json import dumps
from re import search, sub

__REGION__ = 'us-east-1'


def set_region(region):
    global __REGION__

    __REGION__ = region


def get_queues(queue_name_regex: str = None, region: str = __REGION__):
    """
    This function will return a list of queue information. If a regular expression is provided, only queues with a name
    matching that regular expression are returned, otherwise all queues are returned.

    :param queue_name_regex: A regular expression used to limit the results of this function to queues with a
        matching name.
    :param region: The AWS region.
    :return list of dict: A list of queue information.
    """
    queues = {}

    session = boto3.session.Session()
    client = session.client(
        service_name='batch',
        region_name=region
    )

    response = client.describe_job_queues()
    if response:
        # If queue_name_regex was provided, limit results to those queue names which match.
        queues = [q for q in response.get('jobQueues', {}) if queue_name_regex is None or
                  (queue_name_regex and search(queue_name_regex, q['jobQueueName']))]

    return queues


def get_queue_names(queue_name_regex: str = None, region: str = __REGION__):
    """
    This function will return a list of queue names (no other details about the queues). If a regular expression is
    provided, only queue names matching that regular expression are returned, otherwise all queue names are returned.

    :param queue_name_regex: A regular expression used to limit the results of this function to matching queue names.
    :param region: The AWS region.
    :return list of str: A list of queue names.
    """
    queues = get_queues(queue_name_regex=queue_name_regex, region=region)

    # Get just the queue names and discard all other information.
    queue_names = [q['jobQueueName'] for q in queues]

    return queue_names


def get_jobs(queue_names: list = None, job_name_prefix: str = None, region: str = __REGION__):
    """
    This function will return a list of job information. If a list of queue names is provided, jobs from only those
    queues will be returned. If a job name prefix is specified, only jobs with names beginning with that prefix will
    be returned.

    :param queue_names: A list of queues which will limit the result of this function to jobs in only those queues.
    :param job_name_prefix: Only jobs with a name matching this prefix will be returned.
    :param region: The AWS region.
    :return list of dict:
    """
    jobs = []

    session = boto3.session.Session()
    client = session.client(
        service_name='batch',
        region_name=region
    )

    # If the queue names were not specified, look in all queues.
    if not queue_names:
        queue_names = get_queue_names(region=region)

    # If a job name prefix was specified, use a job name filter to limit the results.
    if job_name_prefix:
        filters = [{'name': 'JOB_NAME', 'values': [f'{job_name_prefix}*']}]
    else:
        # Otherwise, use a very inclusive created date filter to include all jobs, without requiring a call to AWS for
        # each and every job state (which is required if you don't use any filter).
        filters = [{'name': 'AFTER_CREATED_AT', 'values': ['0']}]

    # AWS only lists jobs for a single queue at a time, so loop through all the queues and build a job list.
    for queue_name in queue_names:
        response = client.list_jobs(
            jobQueue=queue_name,
            filters=filters
        )

        if response and isinstance(response, dict):
            jobs.extend(response.get('jobSummaryList', []))

    return jobs


def get_array_jobs(array_job_id: str, region: str = __REGION__):
    """
    This function will return all the "child" array jobs belonging to a "parent" array job.

    :param array_job_id: The job id of the array job "parent".
    :param region: The AWS region.
    :return list of dict:
    """
    array_jobs = []

    session = boto3.session.Session()
    client = session.client(
        service_name='batch',
        region_name=region
    )

    # When requesting ARRAY jobs, AWS does not allow a filter (which is the trick to getting AWS to return jobs
    # regardless of their status), so we're forced to request jobs by status, for each possible status, because if
    # we don't specify a status, only RUNNING jobs will be returned.
    for status in ['SUBMITTED', 'PENDING', 'RUNNABLE', 'STARTING', 'RUNNING', 'SUCCEEDED', 'FAILED']:
        response = client.list_jobs(
            arrayJobId=array_job_id,
            jobStatus=status
        )

        # Keep a running list of the array jobs.
        if response and isinstance(response, dict):
            jobs = response.get('jobSummaryList', [])
            array_jobs.extend(jobs)

    return array_jobs


def get_job_details(job_ids: list, include_array_job_parents: bool = True, include_array_job_children: bool = False,
                    region: str = __REGION__):
    """
    This function returns detailed job information and is able to recurse into array jobs to include the "child" jobs.

    :param job_ids: The ids of jobs to return.
    :param include_array_job_parents: When True, any "parent" array jobs in the job_ids list will be returned. When
        False, they will be excluded. Excluding "parent" array jobs can be useful when only the "child" array jobs are
        relevant.
    :param include_array_job_children: When True, the "child" jobs of any "parent" array jobs in the job_ids list will
        be returned. When False, they will be excluded. This simplifies the retrieval of "child" array jobs since only
        the id of the "parent" job must be known.
    :param region: The AWS region.
    :return list of dict:
    """
    if len(job_ids) > 100:
        raise Exception("A maximum of 100 job_ids may be specified.")

    session = boto3.session.Session()
    client = session.client(
        service_name='batch',
        region_name=region
    )

    response = client.describe_jobs(
        jobs=job_ids
    )

    if response and isinstance(response, dict):
        jobs = response.get('jobs', [])
    else:
        jobs = []

    return jobs


def submit_job(job_name, job_queue, job_definition, depends_on=None, tags=None, container_overrides=None,
               array_properties=None, region: str = __REGION__):
    if depends_on is None:
        depends_on = []

    if tags is None:
        tags = {}

    if container_overrides is None:
        container_overrides = {}

    if array_properties is None:
        array_properties = {}

    # Ensure that the job name contains only valid characters and doesn't exceed the max length of 128.
    job_name = sub('[^a-zA-Z0-9_-]', '_', job_name)[:128]

    logging.info(f'Starting AWS Batch job with parameters: jobName="{job_name}", jobQueue="{job_queue}", jobDefinition="{job_definition}"')

    batch = boto3.client(
        service_name='batch',
        region_name=region
    )

    job = batch.submit_job(
        jobName=job_name,
        jobQueue=job_queue,
        jobDefinition=job_definition,
        dependsOn=depends_on,
        tags=tags,
        propagateTags=True,
        containerOverrides=container_overrides,
        arrayProperties=array_properties
    )

    logging.info(f'Started job: {job}')

    return job


if __name__ == '__main__':
    # print(dumps(get_queue_names(queue_name_regex=".*amd.+model.*run.*"), indent=4))
    # print(dumps(get_queue_names(queue_name_regex=".*amd.*"), indent=4))
    # print(dumps(get_queue_names(queue_name_regex="amd"), indent=4))
    # print(dumps(get_queue_names(queue_name_regex="blah"), indent=4))
    # print(dumps(get_queue_names(), indent=4))

    # print(dumps(get_queues(queue_name_regex=".*amd.+model.*run.*"), indent=4))
    # print(dumps(get_queues(queue_name_regex=".*amd.*"), indent=4))
    # print(dumps(get_queues(queue_name_regex="amd"), indent=4))
    # print(dumps(get_queues(queue_name_regex="blah"), indent=4))
    # print(dumps(get_queues(), indent=4))

    # print(dumps(get_jobs(), indent=4))
    # print(dumps(get_jobs(job_name_prefix='run_all_fleets'), indent=4))
    # print(dumps(get_jobs(job_name_prefix='run_all_fleets__20220223_124039'), indent=4))

    # job_ids = [j['jobId'] for j in get_jobs(job_name_prefix='run_all_fleets__20220223_124039')]
    # print(dumps(get_job_details(job_ids=job_ids), indent=4))

    # print(dumps(get_array_jobs(array_job_id='08884c85-9a14-49d7-815a-0c0ba55eb80e'), indent=4))

    j = get_jobs()

    pass
