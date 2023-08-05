from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import yaml

from fiddler.core_objects import BatchPublishType, Column, DatasetInfo, FiddlerTimestamp
from fiddler.utils import logging
from fiddler.v2.api.api import Client
from fiddler.v2.constants import FiddlerTimestamp as V2FiddlerTimestamp
from fiddler.v2.constants import FileType
from fiddler.v2.schema.common import Column as V2Column
from fiddler.v2.schema.common import DatasetInfo as V2DatasetInfo
from fiddler.v2.schema.dataset import Dataset

DATASET_MAX_ROWS = 50_000


logger = logging.getLogger(__name__)


class V1V2Compat:
    def __init__(self, client_v2: Client):
        self.client_v2 = client_v2

    # Projects
    def get_projects(self, get_project_details: bool = False) -> List[str]:
        """List the ids of all projects in the organization.

        :param get_project_details: Unused argument to maintain compatibility
        :returns: List of strings containing the ids of each project.
        """
        projects = self.client_v2.get_projects()
        return [p.name for p in projects]

    def add_project(self, project_id: str) -> Dict[str, str]:
        """Create a new project.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine. Must be a short string without whitespace.

        :returns: Server response for creation action.
        """
        project = self.client_v2.add_project(project_name=project_id)
        return {'project_name': project.name}

    def delete_project(self, project_id: str) -> None:
        """Permanently delete a project.

        :param project_id: The unique identifier of the project on the Fiddler
            engine.

        :returns: None
        """
        self.client_v2.delete_project(project_name=project_id)

    # Datasets
    def get_datasets(self, project_id: str) -> List[str]:
        """List the ids of all datasets in the organization.

        :param project_id: The unique identifier of the project on Fiddler
        :returns: List of strings containing the ids of each dataset.
        """
        datasets = self.client_v2.get_datasets(project_name=project_id)
        return [d.name for d in datasets]

    def get_dataset_artifact(
        self,
        project_id: str,
        dataset_id: str,
        max_rows: int = 1_000,
        splits: Optional[List[str]] = None,
        sampling=False,
        dataset_info: Optional[DatasetInfo] = None,
        include_fiddler_id=False,
    ) -> Dict[str, pd.DataFrame]:
        raise NotImplementedError('This method is currently not implemented')

    def get_dataset(self, project_id: str, dataset_id: str) -> Dataset:
        dataset = self.client_v2.get_dataset(
            project_name=project_id, dataset_name=dataset_id
        )
        return dataset  # @todo: Make the response compatible with dataset info

    def get_dataset_info(self, project_id: str, dataset_id: str) -> DatasetInfo:
        """Get DatasetInfo for a dataset.

        :param project_id: The unique identifier of the project on Fiddler
        :param dataset_id: The unique identifier of the dataset on the Fiddler
            engine.

        :returns: A fiddler.DatasetInfo object describing the dataset.
        """
        dataset = self.get_dataset(project_id, dataset_id)
        dataset_info = DatasetInfo(
            display_name=dataset.name,
            columns=[
                Column.from_dict(col.dict(by_alias=True))
                for col in dataset.info.columns
            ],
            dataset_id=dataset_id,
        )
        return dataset_info

    def delete_dataset(self, project_id: str, dataset_id: str) -> None:
        """Permanently delete a dataset.

        :param project_id: The unique identifier of the project on the Fiddler
            engine.
        :param dataset_id: The unique identifier of the dataset on the Fiddler
            engine.

        :returns: None
        """
        # @todo: FDL-5366
        # check that on the server side
        # 1. Delete the table in CH
        # 2. Delete the files from blob store
        # 3. Delete the entry from postgres table
        self.client_v2.delete_dataset(project_name=project_id, dataset_name=dataset_id)

    # Uploading Dataset
    def upload_dataset_dataframe(
        self,
        project_id: str,
        dataset: Dict[str, pd.DataFrame],
        dataset_id: str,
        info: Optional[DatasetInfo] = None,
        size_check_enabled: bool = True,
    ) -> Dict[str, str]:
        """Uploads a representative dataset to the Fiddler engine.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param dataset: A dictionary mapping name -> DataFrame
            containing data to be uploaded to the Fiddler engine.
        :param dataset_id: The unique identifier of the dataset on the Fiddler
            engine. Must be a short string without whitespace.
        :param info: A DatasetInfo object specifying all the details of the
            dataset.
        :param size_check_enabled: Unused argument to maintain compatibility

        :returns: The server response for the upload.
        """
        v2_info = None
        if info:
            v2_info = V2DatasetInfo(
                columns=[V2Column.from_dict(col.to_dict()) for col in info.columns]
            )

        return self.client_v2.upload_dataset_dataframe(
            project_name=project_id,
            dataset_name=dataset_id,
            datasets=dataset,
            info=v2_info,
            is_sync=True,
        )

    def upload_dataset(
        self,
        project_id: str,
        dataset_id: str,
        file_path: str,
        file_type: str = 'csv',
        file_schema=Dict[str, Any],
        info: Optional[DatasetInfo] = None,
        size_check_enabled: bool = False,
    ) -> Dict[str, str]:
        """Uploads a representative dataset to the Fiddler engine from directory.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param dataset_id: The unique identifier of the dataset on the Fiddler
            engine. Must be a short string without whitespace.
        :param file_path: str pointing to the dataset to be uploaded
        :param file_type: str representing the file type of the uploading dataset. Supported type 'csv'
        :param file_schema: <TBD>
        :param info: A DatasetInfo object specifying all the details of the
            dataset.
        :param size_check_enabled: Unused argument to maintain compatibility

        :returns: The server response for the upload.
        """
        file_name = file_path.split('/')[-1]
        files = {file_name: Path(file_path)}
        # @todo as we only support csv on server side for now, throw an error saying the same.
        v2_info = None
        if info:
            v2_info = V2DatasetInfo(
                columns=[V2Column.from_dict(col.to_dict()) for col in info.columns]
            )
        if file_type == 'csv':
            return self.client_v2.upload_dataset(
                project_name=project_id,
                dataset_name=dataset_id,
                files=files,
                info=v2_info,
                file_type=FileType.CSV,
                file_schema=file_schema,
            )
        else:
            raise NotImplementedError('Only csv is supported in current implementation')

    def upload_dataset_dir(
        self,
        project_id: str,
        dataset_id: str,
        dataset_dir: Path,
        file_type: str = 'csv',
        file_schema=None,
        size_check_enabled: bool = False,
    ) -> Dict[str, str]:
        # Input checks
        if file_type != 'csv':
            raise NotImplementedError('Only CSV filetype is supported')

        if not dataset_dir.is_dir():
            raise ValueError(f'{dataset_dir} is not a directory')

        dataset_yaml = dataset_dir / f'{dataset_id}.yaml'
        if not dataset_yaml.is_file():
            raise ValueError(f'Dataset YAML file not found: {dataset_yaml}')

        with dataset_yaml.open() as f:
            dataset_info = DatasetInfo.from_dict(yaml.safe_load(f))

        # Convert files into dataframes
        files = dataset_dir.glob(f'*.{FileType.CSV}')
        csv_files = [x for x in files if x.is_file()]

        dataset = {}
        csv_paths = []
        for file in csv_files:
            csv_name = str(file).split('/')[-1]
            csv_paths.append(csv_name)
            name = csv_name[:-4]

            # @TODO Change the flow so that we can read the CSV in chunks
            dataset[name] = pd.read_csv(file, dtype=dataset_info.get_pandas_dtypes())

        # size check
        size_exceeds = False
        for name, df in dataset.items():
            if df.shape[0] > DATASET_MAX_ROWS:
                size_exceeds = True
        if size_exceeds:
            raise RuntimeError(
                f'Dataset upload aborted as size exceeds {DATASET_MAX_ROWS}.'
            )

        return self.upload_dataset_dataframe(
            project_id=project_id,
            dataset_id=dataset_id,
            dataset=dataset,
            info=dataset_info,
            size_check_enabled=size_check_enabled,
        )

    def upload_dataset_from_dir(
        self,
        project_id: str,
        dataset_id: str,
        dataset_dir: Path,
        file_type: str = 'csv',
        file_schema=None,
        size_check_enabled: bool = False,
    ) -> Dict[str, str]:
        """Uploads a representative dataset to the Fiddler engine from directory.

        :param project_id: The unique identifier of the model's project on the
            Fiddler engine.
        :param dataset_id: The unique identifier of the dataset on the Fiddler
            engine. Must be a short string without whitespace.
        :param dataset_dir: pathlib.Path pointing to the dir that contains the dataset
            and dataset info yaml to be uploaded.
        :param file_type: File type of the dataset being uploaded. Supported type: 'csv'
        :param file_schema: <TBD>
        :param size_check_enabled: Unused argument to maintain compatibility

        :returns: The server response for the upload.
        """
        if file_type != 'csv':
            raise NotImplementedError('Only CSV filetype is supported')

        info_yaml = dataset_dir / f'{dataset_id}.yaml'

        if not info_yaml.exists():
            raise ValueError(f'DatasetInfo yaml ({info_yaml}) not found.')

        with open(info_yaml) as f:
            dataset_info = DatasetInfo.from_dict(yaml.safe_load(f))

        v2_info = V2DatasetInfo(
            columns=[V2Column.from_dict(col.to_dict()) for col in dataset_info.columns]
        )

        return self.client_v2.upload_dataset_from_dir(
            project_id,
            dataset_id,
            dataset_dir,
            v2_info,
            FileType.CSV,
            file_schema,
            is_sync=True,
        )
        
    def publish_events_batch_schema(
        self, 
        batch_source: Union[Path, str], 
        publish_schema: Dict[str, Any], 
        data_source: Optional[BatchPublishType] = None,
    ) -> None:
        return self.client_v2.publish_events_batch_schema(batch_source, publish_schema, data_source)

    def publish_events_batch(  # noqa
        self,
        project_id: str,
        model_id: str,
        batch_source: Union[pd.DataFrame, str],
        id_field: Optional[str] = None,
        update_event: Optional[bool] = False,
        timestamp_field: Optional[str] = None,
        timestamp_format: FiddlerTimestamp = FiddlerTimestamp.INFER,
        data_source: Optional[BatchPublishType] = None,
        casting_type: Optional[bool] = False,
        credentials: Optional[dict] = None,
        group_by: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Publishes a batch events object to Fiddler Service.
        :param project_id:    The project to which the model whose events are being published belongs.
        :param model_id:      The model whose events are being published.
        :param batch_source:  Batch object to be published. Can be one of: Pandas DataFrame, CSV file
        :param id_field:  Column to extract id value from.
        :param update_event: Bool indicating if the events are updates to previously published rows
        :param timestamp_field:     Column to extract timestamp value from.
                              Timestamp must match the specified format in `timestamp_format`.
        :param timestamp_format:   Format of timestamp within batch object. Can be one of:
                                - FiddlerTimestamp.INFER
                                - FiddlerTimestamp.EPOCH_MILLISECONDS
                                - FiddlerTimestamp.EPOCH_SECONDS
                                - FiddlerTimestamp.ISO_8601
        :param data_source:   Source of batch object. In case of failed inference, can be one of:
                                - BatchPublishType.DATAFRAME
                                - BatchPublishType.LOCAL_DISK
                                - BatchPublishType.AWS_S3
                                - BatchPublishType.GCP_STORAGE
        :param casting_type: Unused argument to maintain compatibility
        :param credentials: Unused argument to maintain compatibility
        :param group_by: Column to group events together for Model Performance metrics. For example,
                         in ranking models that column should be query_id or session_id, used to
                         compute NDCG and MAP. Be aware that the batch_source file/dataset provided should have
                         events belonging to the SAME query_id/session_id TOGETHER and cannot be mixed
                         in the file. For example, having a file with rows belonging to query_id 31,31,31,2,2,31,31,31
                         would not work. Please sort the file by group_by group first to have rows with
                         the following order: query_id 31,31,31,31,31,31,2,2.
        """
        v2_timestamp_format = V2FiddlerTimestamp(timestamp_format.value)
        if type(batch_source) == pd.DataFrame and (
            data_source is None or BatchPublishType.DATAFRAME == data_source
        ):
            return self.client_v2.publish_events_batch_dataframe(
                project_name=project_id,
                model_name=model_id,
                events_df=batch_source,
                id_field=id_field,
                is_update=update_event,
                timestamp_field=timestamp_field,
                timestamp_format=v2_timestamp_format,
                group_by=group_by,
                is_sync=True,
            )
        elif type(batch_source) == str and (
            data_source is None or BatchPublishType.LOCAL_DISK == data_source
        ):
            return self.client_v2.publish_events_batch(
                project_name=project_id,
                model_name=model_id,
                events_path=Path(batch_source),
                id_field=id_field,
                is_update=update_event,
                timestamp_field=timestamp_field,
                timestamp_format=v2_timestamp_format,
                group_by=group_by,
                file_type=FileType.CSV,
                is_sync=True,
            )
        else:
            raise NotImplementedError(
                'Batch source other than dataframe and csv is not implemented now'
            )

    def publish_event(
        self,
        project_id: str,
        model_id: str,
        event: dict,
        event_id: Optional[str] = None,
        update_event: Optional[bool] = None,
        event_timestamp: Optional[int] = None,
        timestamp_format: FiddlerTimestamp = FiddlerTimestamp.INFER,
        casting_type: Optional[bool] = False,
        dry_run: Optional[bool] = False,
    ) -> str:
        """
        Publishes an event to Fiddler Service.
        :param project_id: The project to which the model whose events are being published belongs
        :param model_id: The model whose events are being published
        :param dict event: Dictionary of event details, such as features and predictions.
        :param event_id: Unique str event id for the event
        :param update_event: Bool indicating if the event is an update to a previously published row
        :param event_timestamp: The UTC timestamp of the event in epoch milliseconds (e.g. 1609462800000)
        :param timestamp_format:   Format of timestamp within batch object. Can be one of:
                                - FiddlerTimestamp.INFER
                                - FiddlerTimestamp.EPOCH_MILLISECONDS
                                - FiddlerTimestamp.EPOCH_SECONDS
                                - FiddlerTimestamp.ISO_8601
        :param casting_type: Unused argument to maintain compatibility
        :param dry_run: Unused argument to maintain compatibility

        """
        v2_timestamp_format = V2FiddlerTimestamp(timestamp_format.value)
        return self.client_v2.publish_event(
            project_name=project_id,
            model_name=model_id,
            event=event,
            event_id=event_id,
            is_update=update_event,
            event_timestamp=event_timestamp,
            timestamp_format=v2_timestamp_format,
        )
