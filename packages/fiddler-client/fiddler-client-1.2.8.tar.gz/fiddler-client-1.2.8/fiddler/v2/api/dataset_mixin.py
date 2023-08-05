import json
import os
import tempfile
from http import HTTPStatus
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from pydantic import parse_obj_as

from fiddler.libs.http_client import RequestClient
from fiddler.utils import logging
from fiddler.v2.api.helpers import multipart_upload
from fiddler.v2.constants import FileType, UploadType
from fiddler.v2.schema.common import DatasetInfo
from fiddler.v2.schema.dataset import Dataset, DatasetIngest
from fiddler.v2.utils.exceptions import FiddlerAPIException, handle_api_error_response
from fiddler.v2.utils.response_handler import (
    APIResponseHandler,
    PaginatedResponseHandler,
)

logger = logging.getLogger(__name__)


class DatasetMixin:
    client: RequestClient
    organization_name: str

    @handle_api_error_response
    def get_datasets(self, project_name: str) -> List[Dataset]:
        """
        Get all the datasets in a project

        :param project_name:    The project for which you want to get the datasets
        :returns:               A list containing `Dataset` objects.
        """
        response = self.client.get(
            url='datasets',
            params={
                'organization_name': self.organization_name,
                'project_name': project_name,
            },
        )
        _, items = PaginatedResponseHandler(response).get_pagination_details_and_items()
        return parse_obj_as(List[Dataset], items)

    @handle_api_error_response
    def get_dataset(self, project_name: str, dataset_name: str) -> Dataset:
        """
        Get all the details for a given dataset

        :param project_name:    The project to which the dataset belongs to
        :param dataset_name:    The dataset name of which you need the details

        :returns: Dataset object which contains the details
        """

        response = self.client.get(
            url=f'datasets/{self.organization_name}:{project_name}:{dataset_name}',
        )
        response_handler = APIResponseHandler(response)
        return Dataset.deserialize(response_handler)

    @handle_api_error_response
    def add_dataset(
        self,
        name: str,
        project_name: str,
        info: Optional[DatasetInfo] = None,
    ) -> Dataset:
        request_body = dict(
            name=name,
            project_name=project_name,
            organization_name=self.organization_name,
            info=info,
        )

        response = self.client.post(
            url='datasets',
            data=request_body,
        )
        logger.info(f'{name} dataset created')
        return Dataset.deserialize(APIResponseHandler(response))

    @handle_api_error_response
    def delete_dataset(self, project_name: str, dataset_name: str) -> None:
        """
        Delete a dataset

        :param project_name:    The project to which the dataset belongs to
        :param dataset_name:    The dataset name which you want to delete

        :returns: None
        """

        response = self.client.delete(
            url=f'datasets/{self.organization_name}:{project_name}:{dataset_name}',
        )
        if response.status_code == HTTPStatus.OK:
            logger.info(f'{dataset_name} deleted successfully.')
        else:
            # @TODO: Handle non 200 status response
            logger.info('Delete unsuccessful')

    @handle_api_error_response
    def upload_dataset(
        self,
        project_name: str,
        dataset_name: str,
        files: Dict[str, Path],
        info: Optional[DatasetInfo] = None,
        file_type: Optional[FileType] = None,
        file_schema: Optional[dict] = None,
        is_sync: Optional[bool] = True,
    ) -> Dict[str, str]:
        """
        Upload a dataset.

        :param project_name:    The project to which the dataset belongs to
        :param dataset_name:    Dataset name used for upload
        :param files:           A dictionary of file name and key and file path as value. Eg `{'train': pathlib.Path('datasets/train.csv')}`
        :param info:            DatasetInfo object
        :param file_type:       FileType which specifices the filetype csv etc.
        :param file_schema:     <TBD>
        :param is_sync:         A boolean value which determines if the upload method works in synchronous mode or async mode

        :returns:               Dictionary containing details of the job used to publish events incase of 202 response from the server.
        """
        file_names = []
        for _, file_path in files.items():
            _, file_name = os.path.split(file_path)
            response = multipart_upload(
                client=self.client,
                organization_name=self.organization_name,
                project_name=project_name,
                identifier=dataset_name,
                upload_type=UploadType.DATASET.value,
                file_path=str(file_path),
                file_name=file_name,
            )
            file_names.append(response.get('file_name'))

        request_body = DatasetIngest(
            name=dataset_name,
            file_name=file_names,
            info=info,
            file_type=file_type,
            file_schema=file_schema,
        ).dict(
            by_alias=True
        )  # setting by_alias bc Columns fiels are aliased
        response = self.client.post(
            url=f'datasets/{self.organization_name}:{project_name}:{dataset_name}/ingest',
            data=json.dumps(request_body),
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
            logger.error(f'Failed to upload dataset {dataset_name}.')
            raise FiddlerAPIException(
                response.status_code,
                error_code=response.status_code,
                message=response.content,
                errors=[],
            )

    @handle_api_error_response
    def upload_dataset_csv(
        self,
        project_name: str,
        dataset_name: str,
        files: Dict[str, Path],
        info: Optional[DatasetInfo] = None,
        file_schema: Optional[dict] = None,
        is_sync: Optional[bool] = True,
    ) -> Dict[str, str]:
        """
        Upload dataset as csv file

        :param project_name:    The project to which the dataset belongs to
        :param dataset_name:    Dataset name used for upload
        :param files:           A dictionary of pathlib.Path as value and name as key. Eg `{'train': pathlib.Path('datasets/train.csv')}`
        :param info:            DatasetInfo object
        :param is_sync:         A boolean value which determines if the upload method works in synchronous mode or async mode

        :returns:               Dictionary containing details of the job used to publish events incase of 202 response from the server.
        """
        if not files:
            raise ValueError('`files` is empty. Please enter a valid input')

        return self.upload_dataset(
            project_name, dataset_name, files, info, FileType.CSV, file_schema, is_sync
        )

    @handle_api_error_response
    def upload_dataset_dataframe(
        self,
        project_name: str,
        dataset_name: str,
        datasets: Dict[str, pd.DataFrame],
        info: Optional[DatasetInfo] = None,
        is_sync: Optional[bool] = True,
    ) -> Dict[str, str]:
        """
        Upload dataset as pd.DdataFrame

        :param project_name:    The project to which the dataset belongs to
        :param dataset_name:    Dataset name used for upload
        :param datasets:        A dictionary of dataframe as value and name as key. Eg `{'train': train_df}`
        :param info:            DatasetInfo object
        :param is_sync:         A boolean value which determines if the upload method works in synchronous mode or async mode

        :returns:               Dictionary containing details of the job used to publish events incase of 202 response from the server.
        """
        if not datasets:
            raise ValueError('`datasets` is empty. Please enter a valid dataset')

        with tempfile.TemporaryDirectory() as tmp:
            files = {}
            file_type = FileType.CSV
            for name, df in datasets.items():
                file_path = Path(tmp) / f'{name}{file_type}'
                df.to_csv(file_path, index=False)
                files.update({name: file_path})

            return self.upload_dataset(
                project_name,
                dataset_name,
                files=files,
                info=info,
                file_type=file_type,
                is_sync=is_sync,
            )

    @handle_api_error_response
    def upload_dataset_from_dir(
        self,
        project_name: str,
        dataset_name: str,
        dataset_dir: Path,
        info: Optional[DatasetInfo] = None,
        file_type: FileType = FileType.CSV,
        file_schema: Optional[dict] = None,
        is_sync: bool = True,
    ) -> Dict[str, str]:
        """
        Upload dataset artefacts (data file and dataset info yaml) from a directory

        :param project_name:    The project to which the dataset belongs to
        :param dataset_name:    Dataset name used for upload
        :param dataset_dir:     pathlib.Path pointing to the dataset dir to be uploaded
        :param info:            DatasetInfo object
        :param file_type:       FileType
        :param file_schema:     <TBD>
        :param is_sync:         A boolean value which determines if the upload method works in synchronous mode or async mode

        :returns:               Dictionary containing details of the job used to publish events incase of 202 response from the server.
        """
        # @TODO: Move repetative input validation used accross different methods to utils
        if not dataset_dir.is_dir():
            raise ValueError(f'{dataset_dir} is not a directory')

        files = {
            data_file.name: data_file
            for data_file in dataset_dir.glob(f'*{file_type.value}')
        }

        if not files:
            raise ValueError(f'No data files found in {dataset_dir}.')

        return self.upload_dataset(
            project_name=project_name,
            dataset_name=dataset_name,
            files=files,
            info=info,
            file_schema=file_schema,
            is_sync=is_sync,
        )
