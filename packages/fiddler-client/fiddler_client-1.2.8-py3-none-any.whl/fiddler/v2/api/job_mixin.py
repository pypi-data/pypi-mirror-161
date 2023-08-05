import time
from http import HTTPStatus
from typing import List, Optional

from requests.exceptions import ConnectionError

from fiddler.libs.http_client import RequestClient
from fiddler.utils import logging
from fiddler.v2.schema.job import JobStatus
from fiddler.v2.utils.exceptions import handle_api_error_response
from fiddler.v2.utils.response_handler import JobResponseHandler

logger = logging.getLogger(__name__)


class JobMixin:
    client: RequestClient
    organization_name: str

    @handle_api_error_response
    def get_job(self, uuid: str) -> Optional[JobResponseHandler]:
        """
        Get details about a job

        :params uuid: Unique identifier of the job to get the details of
        :returns: JobResponseHandler object containing details
        """
        # Setting timeout as makeshift approach to handle pod restart
        # leading the ConnectionResetError on client
        timeout = 120
        response = self.client.get(url=f'jobs/{uuid}', timeout=timeout)
        if response.status_code == HTTPStatus.OK:
            return JobResponseHandler(response)
        else:
            # @TODO we should throw error here instead of logging
            logger.info(f'Response status code: {response.status_code}')
            logger.info(response.body)

    def poll_job(self, uuid: str, interval: int = 3) -> JobResponseHandler:
        """
        Poll an ongoing job. This method will keep polling until a job has SUCCESS, FAILURE, RETRY, REVOKED status.
        Will return a JobResponseHandler object once the job has ended.

        :params uuid: Unique identifier of the job to keep polling
        :params interval: Interval in sec between two subsequent poll calls. Default is 1sec
        :returns: JobResponseHandler object containing job details.
        """
        job = self.get_job(uuid)
        # @TODO: Set max iteration limit?
        while job.status in [JobStatus.PENDING, JobStatus.STARTED]:
            # @TODO: show proper message
            logger.info(
                f'JOB UUID: {uuid} status: {job.status} Progress: {job.progress:.2f}'
            )

            time.sleep(interval)
            try:
                job = self.get_job(uuid)
            except ConnectionError:
                logger.exception(
                    'Failed to connect to the server. Retrying...\nIf this error persists, please reach out to Fiddler.'
                )

        if job.status == JobStatus.FAILURE:
            logger.error(
                f"JOB UUID: {uuid} failed with error message '{job.error_message}'"
            )

        logger.info(
            f'JOB UUID: {uuid} status: {job.status} Progress: {job.progress:.2f}'
        )
        return job

    @staticmethod
    def get_task_results(job: JobResponseHandler) -> List[str]:
        results: List[str] = []
        if not job.extras:
            return results
        for task_id, extra_info in job.extras.items():
            if not extra_info['result']:
                continue
            results.append(
                f'JOB UUID: {job.uuid} task id: {task_id} result: {extra_info["result"]}'
            )
        return results
