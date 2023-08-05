import time
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional

from tecton._internals import metadata_service
from tecton_proto.materialization.materialization_states_pb2 import _MATERIALIZATIONTASKATTEMPTSTATE
from tecton_proto.materialization.materialization_states_pb2 import _MATERIALIZATIONTASKSTATE
from tecton_proto.metadataservice.metadata_service_pb2 import CancelJobRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetJobRequest
from tecton_proto.metadataservice.metadata_service_pb2 import JobAttempt
from tecton_proto.metadataservice.metadata_service_pb2 import ListJobsRequest
from tecton_proto.metadataservice.metadata_service_pb2 import MaterializationJob
from tecton_proto.metadataservice.metadata_service_pb2 import MaterializationJobRequest

ATTEMPT_STATE_PREFIX = "MATERIALIZATION_ATTEMPT_STATUS_"
TASK_STATE_PREFIX = "MATERIALIZATION_TASK_STATUS_"


class MaterializationTimeoutException(Exception):
    pass


class MaterializationJobFailedException(Exception):
    pass


@dataclass
class MaterializationAttemptData:
    """Materialization Attempt data

    Data representation of the materialization attempt.
    Materialization job may have multiple attempts to materialize features.

    Attributes:
        id (int): materialization attempt id
        run_url (str): url to track attempts
        state (str): run state of the attempt
        created_at (datetime): attempt creation time
        updated_at (datetime): attempt update time
    """

    id: str
    run_url: str
    state: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_proto(cls, proto: JobAttempt):
        parsed_state = _MATERIALIZATIONTASKATTEMPTSTATE.values_by_number[proto.state].name
        trimmed_state = (
            parsed_state[len(ATTEMPT_STATE_PREFIX) :] if parsed_state.startswith(ATTEMPT_STATE_PREFIX) else parsed_state
        )
        created_at = datetime.utcfromtimestamp(proto.created_at.seconds)
        updated_at = datetime.utcfromtimestamp(proto.updated_at.seconds)
        return cls(
            id=proto.id, run_url=proto.run_url, state=trimmed_state, created_at=created_at, updated_at=updated_at
        )


@dataclass
class MaterializationJobData:
    """Materialization Job data

    Data representation of the materialization job

    Attributes:
        id (int): materialization job id
        workspace (str): project workspace
        feature_view (str): feature_view that is being materialized
        state (str): run state of the job
        online (bool): does this materialize in the online store
        offline (bool): does this materialize in the offline store
        start_time (datetime): start timestamp of the materialization window
        end_time (datetime): end timestamp of the materialization window
        created_at (datetime): job creation time
        updated_at (datetime): job update time
        attempts (List[MaterializationAttemptData]): feature materialization attempts
        next_attempt_at (Optional[datetime]): time when next materialization attempt will start
    """

    id: str
    workspace: str
    feature_view: str
    state: str
    online: bool
    offline: bool
    start_time: datetime
    end_time: datetime
    created_at: datetime
    updated_at: datetime
    attempts: List[MaterializationAttemptData]
    next_attempt_at: Optional[datetime]

    @classmethod
    def from_proto(cls, proto: MaterializationJob):
        parsed_state = _MATERIALIZATIONTASKSTATE.values_by_number[proto.state].name
        trimmed_state = (
            parsed_state[len(TASK_STATE_PREFIX) :] if parsed_state.startswith(TASK_STATE_PREFIX) else parsed_state
        )
        start_time = datetime.utcfromtimestamp(proto.start_time.seconds)
        end_time = datetime.utcfromtimestamp(proto.end_time.seconds)
        created_at = datetime.utcfromtimestamp(proto.created_at.seconds)
        updated_at = datetime.utcfromtimestamp(proto.updated_at.seconds)
        attempts = [MaterializationAttemptData.from_proto(attempt_proto) for attempt_proto in proto.attempts]
        next_attempt_at = (
            datetime.utcfromtimestamp(proto.next_attempt_at.seconds) if proto.HasField("next_attempt_at") else None
        )
        return cls(
            id=proto.id,
            workspace=proto.workspace,
            feature_view=proto.feature_view,
            state=trimmed_state,
            online=proto.online,
            offline=proto.offline,
            start_time=start_time,
            end_time=end_time,
            created_at=created_at,
            updated_at=updated_at,
            attempts=attempts,
            next_attempt_at=next_attempt_at,
        )


def trigger_materialization_job(
    feature_view: str,
    workspace: str,
    start_time: datetime,
    end_time: datetime,
    online: bool,
    offline: bool,
    use_tecton_managed_retries: bool = True,
    overwrite: bool = False,
) -> str:
    """
    Kicks off a materialization job. Can throw validation errors.

    :param feature_view: feature view name that's going to be materialized
    :param workspace: project workspace string
    :param start_time: start time of the materialization window
    :param end_time: end time of the materialization window
    :param online: is materializing features to the online store
    :param offline: is materialization features to the offline store
    :param tecton_managed_retries: is retries managed by tecton
    :param overwrite: is allowed to kick off job if successful materialization already exists with the same window
    :return: string ID of the materialization job
    """
    request = MaterializationJobRequest()
    request.feature_view = feature_view
    request.workspace = workspace
    request.start_time.FromDatetime(start_time)
    request.end_time.FromDatetime(end_time)
    request.online = online
    request.offline = offline
    request.use_tecton_managed_retries = use_tecton_managed_retries
    request.overwrite = overwrite

    mds_instance = metadata_service.instance()
    response = mds_instance.SubmitMaterializationJob(request)
    return response.job.id


def list_materialization_jobs(feature_view: str, workspace: str) -> List[MaterializationJobData]:
    """
    Retrieves all the materialization jobs for the feature_view

    :param feature_view: feature view name that the jobs belong to
    :param workspace: project workspace string
    :return: list of materialization job data
    """
    request = ListJobsRequest()
    request.feature_view = feature_view
    request.workspace = workspace

    mds_instance = metadata_service.instance()
    response = mds_instance.ListMaterializationJobs(request)
    return [MaterializationJobData.from_proto(job) for job in response.jobs]


def get_materialization_job(job_id: str) -> MaterializationJobData:
    """
    Retrieves a materialization job by the id

    data includes materialization attempts

    :param job_id: ID string of the materialization job
    :return: materialization job data
    """
    request = GetJobRequest()
    request.job_id = job_id

    mds_instance = metadata_service.instance()
    response = mds_instance.GetMaterializationJob(request)
    return MaterializationJobData.from_proto(response.job)


def cancel_materialization_job(job_id: str) -> MaterializationJobData:
    """
    Cancels a materialization job by the id

    Job run state will be MANUAL_CANCELLATION_REQUESTED

    :param job_id: ID string of the materialization job
    :return: cancelled materialization job data
    """
    request = CancelJobRequest()
    request.job_id = job_id

    mds_instance = metadata_service.instance()
    response = mds_instance.CancelMaterializationJob(request)
    return MaterializationJobData.from_proto(response.job)


def wait_for_materialization_job(
    job_id: str,
    timeout: Optional[timedelta] = None,
) -> MaterializationJobData:
    """
    blocks until materialization job completion
    can raise exceptions: MaterializationJobFailedException

    :param job_id: ID string of the materialization job
    :param timeout: (Optional) timeout for this function
    :return: string ID of the materialization job
    :raises MaterializationTimeoutException: if timeout param is specified
    :raises MaterializationJobFailedException: materialization job did not reach a successful state
    """
    wait_start_time = datetime.now()
    while True:
        job_data = get_materialization_job(job_id)
        run_state = job_data.state

        if run_state == "SUCCESS":
            return job_data
        elif timeout and ((datetime.now() - wait_start_time) > timeout):
            raise MaterializationTimeoutException(f"job {job_id} timed out, last job state {run_state}")
        elif run_state == "RUNNING":
            time.sleep(60)
        else:
            raise MaterializationJobFailedException(f"job {job_id} failed, last job state {run_state}")
