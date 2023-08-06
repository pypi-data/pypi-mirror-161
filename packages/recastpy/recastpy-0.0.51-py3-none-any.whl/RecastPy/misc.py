def datetime_from_string(date_string):
    from dateutil.parser import parse
    return parse(date_string)


def build_job_name_prefix(dag_id, execution_date, fleet_id=None):
    fleet_id = "" if fleet_id is None else f"{fleet_id}__"

    if isinstance(execution_date, str):
        execution_date = datetime_from_string(execution_date)

    prefix = f'{dag_id}__{execution_date.strftime("%Y%m%d_%H%M%S")}__{fleet_id}'

    return prefix


def build_job_name(dag_id, execution_date, fleet_id=None, suffix=None):
    suffix = "" if suffix is None else f"__{suffix}"

    return f'{build_job_name_prefix(dag_id, execution_date, fleet_id)}{suffix}'
