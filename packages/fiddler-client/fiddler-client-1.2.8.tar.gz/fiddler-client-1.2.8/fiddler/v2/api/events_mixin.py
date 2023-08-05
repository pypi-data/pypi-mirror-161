import json
import tempfile
from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict, Optional, Union
from fiddler.core_objects import BatchPublishType

import pandas as pd
from requests_toolbelt.multipart.encoder import MultipartEncoder

from fiddler.libs.http_client import APP_JSON_CONTENT_TYPE, RequestClient
from fiddler.utils import logging
from fiddler.v2.api.helpers import multipart_upload
from fiddler.v2.constants import FiddlerTimestamp, FileType, UploadType
from fiddler.v2.schema.events import EventIngest, EventsIngest
from fiddler.v2.utils.exceptions import FiddlerAPIException, handle_api_error_response
from fiddler.v2.utils.response_handler import APIResponseHandler

logger = logging.getLogger(__name__)


class EventsMixin:
    client: RequestClient
    organization_name: str

    @handle_api_error_response
    def publish_events_batch(
        self,
        project_name: str,
        model_name: str,
        events_path: Path,
        batch_id: Optional[str] = None,
        events_schema: Optional[str] = None,
        id_field: Optional[str] = None,
        is_update: Optional[bool] = None,
        timestamp_field: Optional[str] = None,
        timestamp_format: Optional[FiddlerTimestamp] = None,
        group_by: Optional[str] = None,
        file_type: Optional[FileType] = None,
        is_sync: Optional[bool] = True,
    ) -> Dict[str, str]:
        """
        Publishes a batch events object to Fiddler Service.

        :param project_name: The project to which the model whose events are being published belongs.
        :param model_name: The model whose events are being published.
        :param events_path: pathlib.Path pointing to the events file to be uploaded
        :param batch_id: <TBD>
        :param events_schema: <TBD>
        :param id_field: Column to extract id value from.
        :param is_update: Bool indicating if the events are updates to previously published rows
        :param timestamp_field: Column to extract timestamp value from.
                                Timestamp must match the specified format in `timestamp_format`.
        :param timestamp_format:Format of timestamp within batch object. Can be one of:
                                - FiddlerTimestamp.INFER
                                - FiddlerTimestamp.EPOCH_MILLISECONDS
                                - FiddlerTimestamp.EPOCH_SECONDS
                                - FiddlerTimestamp.ISO_8601
        :param group_by: Column to group events together for Model Performance metrics. For example,
                        in ranking models that column should be query_id or session_id, used to
                        compute NDCG and MAP. Be aware that the batch_source file/dataset provided should have
                        events belonging to the SAME query_id/session_id TOGETHER and cannot be mixed
                        in the file. For example, having a file with rows belonging to query_id 31,31,31,2,2,31,31,31
                        would not work. Please sort the file by group_by group first to have rows with
                        the following order: query_id 31,31,31,31,31,31,2,2.
        :param file_type: FileType which specifices the filetype csv etc.
        :param is_sync: A boolean value which determines if the upload method works in synchronous mode or async mode
        :returns: Dictionary containing details of the job used to publish events incase of 202 response from the server.
        """
        file_name = events_path.name
        response = multipart_upload(
            client=self.client,
            organization_name=self.organization_name,
            project_name=project_name,
            identifier=model_name,
            upload_type=UploadType.EVENT.value,
            file_path=str(events_path),
            file_name=file_name,
        )
        file_name = response.get('file_name')
        request_body = EventsIngest(
            batch_id=batch_id,
            events_schema=events_schema,
            id_field=id_field,
            is_update=is_update,
            timestamp_field=timestamp_field,
            timestamp_format=timestamp_format,
            group_by=group_by,
            file_type=file_type,
            file_name=[file_name],
        ).dict()
        response = self.client.post(
            url=f'events/{self.organization_name}:{project_name}:{model_name}/ingest',
            data=request_body,
        )
        # @TODO: Handle invalid file path exception
        if response.status_code == HTTPStatus.ACCEPTED:
            resp = APIResponseHandler(response).get_data()
            if is_sync:
                job_id = resp['job_uuid']
                job = self.poll_job(job_id).get_data()
                job.pop('extras', None)
                return job
            else:
                return resp
        else:
            # raising a generic FiddlerAPIException
            logger.error('Failed to publish events')
            raise FiddlerAPIException(
                response.status_code,
                error_code=response.status_code,
                message=response.content,
                errors=[],
            )

    @handle_api_error_response
    def publish_event(
        self,
        project_name: str,
        model_name: str,
        event: dict,
        event_id: Optional[str] = None,
        id_field: Optional[str] = None,
        is_update: Optional[bool] = None,
        event_timestamp: Optional[str] = None,
        timestamp_format: Optional[str] = None,
    ) -> Optional[str]:
        """
        Publishes an event to Fiddler Service.

        :param project_name: The project to which the model whose events are being published belongs
        :param model_name: The model whose events are being published
        :param dict event: Dictionary of event details, such as features and predictions.
        :param event_id: Unique str event id for the event
        :param event_timestamp: The UTC timestamp of the event in epoch milliseconds (e.g. 1609462800000)
        :param timestamp_format: Format of timestamp within batch object. Can be one of:
                                - FiddlerTimestamp.INFER
                                - FiddlerTimestamp.EPOCH_MILLISECONDS
                                - FiddlerTimestamp.EPOCH_SECONDS
                                - FiddlerTimestamp.ISO_8601
        :returns: Unique event id incase of successful submitted request.
        """
        request_body = EventIngest(
            event=event,
            event_id=event_id,
            id_field=id_field,
            is_update=is_update,
            event_timestamp=event_timestamp,
            timestamp_format=timestamp_format,
        ).dict()
        response = self.client.post(
            url=f'events/{self.organization_name}:{project_name}:{model_name}/ingest/event',
            data=request_body,
        )
        if response.status_code == HTTPStatus.ACCEPTED:
            response_dict = APIResponseHandler(response).get_data()
            logger.info(response_dict.get('message'))
            return response_dict.get('__fiddler_id')
        else:
            # raising a generic FiddlerAPIException
            logger.error('Failed to publish events')
            raise FiddlerAPIException(
                response.status_code,
                error_code=response.status_code,
                message=response.content,
                errors=[],
            )

    @handle_api_error_response
    def publish_events_batch_dataframe(
        self,
        project_name: str,
        model_name: str,
        events_df: pd.DataFrame,
        batch_id: Optional[str] = None,
        id_field: Optional[str] = None,
        is_update: Optional[bool] = None,
        timestamp_field: Optional[str] = None,
        timestamp_format: Optional[FiddlerTimestamp] = None,
        group_by: Optional[str] = None,
        is_sync: Optional[bool] = True,
    ) -> Dict[str, str]:
        """
        Publishes a batch events object to Fiddler Service.

        :param project_name: The project to which the model whose events are being published belongs.
        :param model_name: The model whose events are being published.
        :param events_df: pd.DataFrame object having the events
        :param batch_id: <TBD>
        :param id_field: Column to extract id value from.
        :param is_update: Bool indicating if the events are updates to previously published rows
        :param timestamp_field: Column to extract timestamp value from.
                                Timestamp must match the specified format in `timestamp_format`.
        :param timestamp_format: Format of timestamp within batch object. Can be one of:
                                - FiddlerTimestamp.INFER
                                - FiddlerTimestamp.EPOCH_MILLISECONDS
                                - FiddlerTimestamp.EPOCH_SECONDS
                                - FiddlerTimestamp.ISO_8601
        :param group_by: Column to group events together for Model Performance metrics. For example,
                        in ranking models that column should be query_id or session_id, used to
                        compute NDCG and MAP. Be aware that the batch_source file/dataset provided should have
                        events belonging to the SAME query_id/session_id TOGETHER and cannot be mixed
                        in the file. For example, having a file with rows belonging to query_id 31,31,31,2,2,31,31,31
                        would not work. Please sort the file by group_by group first to have rows with
                        the following order: query_id 31,31,31,31,31,31,2,2.
        :param is_sync: A boolean value which determines if the upload method works in synchronous mode or async mode
        :returns: Dictionary containing details of the job used to publish events incase of 202 response from the server.
        """
        file_type = FileType.CSV
        with tempfile.NamedTemporaryFile(suffix=file_type) as temp:
            events_df.to_csv(temp, index=False)
            events_path = Path(temp.name)
            return self.publish_events_batch(
                project_name=project_name,
                model_name=model_name,
                events_path=events_path,
                batch_id=batch_id,
                id_field=id_field,
                is_update=is_update,
                timestamp_field=timestamp_field,
                timestamp_format=timestamp_format,
                group_by=group_by,
                is_sync=is_sync,
            )

    @handle_api_error_response
    def publish_events_batch_schema(  # noqa
        self,
        batch_source: Union[Path, str],
        publish_schema: Dict[str, Any],
        data_source: Optional[BatchPublishType] = None,
        is_sync: Optional[bool] = True,
    ) -> Dict[str, str]:
        """
        Publishes a batch events object to Fiddler Service.
        :param events_path: pathlib.Path pointing to the events file to be uploaded
        :param publish_schema: Dict object specifying layout of data.
        :param is_sync: A boolean value which determines if the upload method works in synchronous mode or async mode
        :returns: Dictionary containing details of the job used to publish events incase of 202 response from the server.
        """
        events_path = batch_source
        request_body_json = {}
        request_body_json['schema'] = publish_schema
        if data_source == BatchPublishType.AWS_S3 and isinstance(events_path, str):
            request_body = {
                's3_url': events_path,
                'schema': json.dumps(publish_schema)
            }
            response = self.client.post(
                url=f'events/{self.organization_name}/ingest/schema',
                headers={'Content-Type': 'application/json'},
                data=request_body,
            )
        else:
            if isinstance(events_path, str):
                events_path = Path(events_path)
            file_name = events_path.name
            files = {}
            files[file_name] = events_path
            request_body = {
                file_path.name: (
                    file_path.name,
                    open(file_path, 'rb'),
                )
                for _, file_path in files.items()
            }
            # https://stackoverflow.com/a/19105672/13201804
            request_body.update(
                {'schema': (None, json.dumps(publish_schema), 'application/json')}
            )
            m = MultipartEncoder(fields=request_body)
            content_type_header, request_body  = m.content_type, m
            # content_type_header, request_body  = event_ingest.multipart_form_request()
            response = self.client.post(
                url=f'events/{self.organization_name}/ingest/schema',
                headers={'Content-Type': content_type_header},
                data=request_body,
            )
        # @TODO: Handle invalid file path exception
        if response.status_code == HTTPStatus.ACCEPTED:
            resp = APIResponseHandler(response).get_data()
            if is_sync:
                job_id = resp['job_uuid']
                job = self.poll_job(job_id).get_data()
                job.pop('extras', None)
                return job
            else:
                return resp

        else:
            # raising a generic FiddlerAPIException
            logger.error('Failed to upload events schema.')
            raise FiddlerAPIException(
                response.status_code,
                error_code=response.status_code,
                message=response.content,
                errors=[],
            )
