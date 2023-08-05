"""
Fiddler Client Module
=====================

A Python client for Fiddler service.

TODO: Add Licence.
"""
import configparser
import functools
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fiddler.api.monitoring import Monitoring
from fiddler.model import Model
from fiddler.project import Project

from . import utils
from ._version import __version__
from .client import Fiddler, PredictionEventBundle
from .core_objects import (
    BatchPublishType,
    Column,
    CustomFeature,
    DatasetInfo,
    DataType,
    DeploymentOptions,
    DeploymentType,
    ExplanationMethod,
    FiddlerPublishSchema,
    FiddlerTimestamp,
    MLFlowParams,
    ModelDeploymentParams,
    ModelInfo,
    ModelInputType,
    ModelTask,
    ArtifactStatus,
)
from .fiddler_api import FiddlerApi as FiddlerApiV1
from .file_processor.src.constants import (
    CSV_EXTENSION,
    PARQUET_COMPRESSION,
    PARQUET_ENGINE,
    PARQUET_EXTENSION,
    PARQUET_ROW_GROUP_SIZE,
)
from .packtools import gem
from .utils import ColorLogger
from .v1_v2_compat import V1V2Compat
from .v2.api.api import Client as FiddlerApiV2
from .v2.constants import ServerDeploymentMode
from .v2.schema.job import JobStatus
from .validator import PackageValidator, ValidationChainSettings, ValidationModule

logger = utils.logging.getLogger(__name__)

VERSIONS = [1, 2]


class FiddlerApi:

    """Client of all connections to the Fiddler API.
    :param url:         The base URL of the API to connect to. Usually either
        https://<yourorg>.fiddler.ai (cloud) or http://localhost:4100 (onebox)
    :param org_id:      The name of your organization in the Fiddler platform
    :param auth_token:  Token used to authenticate. Your token can be
        created, found, and changed at <FIDDLER URL>/settings/credentials.
    :param proxies:     Optionally, a dict of proxy URLs. e.g.,
                    proxies = {'http' : 'http://proxy.example.com:1234',
                               'https': 'https://proxy.example.com:5678'}
    :param verbose:     if True, api calls will be logged verbosely,
                    *warning: all information required for debugging will be
                    logged including the auth_token.
    :param timeout:     How long to wait for the server to respond before giving up
    :param version:     Version of the client you want to instantiate. Options [1,2]
    """

    def __new__(
        cls,
        url: Optional[str] = None,
        org_id: Optional[str] = None,
        auth_token: Optional[str] = None,
        proxies: Optional[dict] = None,
        verbose: Optional[bool] = False,
        timeout: int = 1200,  # sec
        version: int = 1,
    ):
        url, org_id, auth_token = cls._get_connection_parameters(
            cls, url, org_id, auth_token, version
        )

        # Validation of version, org_id is handled by FiddlerApiV1.
        client_v1 = FiddlerApiV1(
            url=url,
            org_id=org_id,
            auth_token=auth_token,
            proxies=proxies,
            verbose=verbose,
            timeout=timeout,
        )
        # @todo: Handle proxies in v2
        client_v2 = FiddlerApiV2(
            url=url, organization_name=org_id, auth_token=auth_token, timeout=timeout
        )
        supported_features = cls._get_supported_features(cls, client_v1, org_id)
        server_deployment_mode = cls._get_server_deployment_mode(
            cls, supported_features
        )

        logger.info(f'Version deployed on the server side {server_deployment_mode}')

        compat_client = V1V2Compat(client_v2)

        if version == 2:
            logger.info('Default client is of client version 2')

            obj = lambda: None  # instantiate an empty object # noqa

            obj.list_datasets = compat_client.get_datasets
            obj.get_dataset_info = compat_client.get_dataset_info
            obj.get_dataset = compat_client.get_dataset_artifact
            obj.delete_dataset = compat_client.delete_dataset

            obj.list_projects = compat_client.get_projects
            obj.create_project = compat_client.add_project
            obj.delete_project = compat_client.delete_project

            obj.upload_dataset = (
                compat_client.upload_dataset_dataframe
            )  # this is uploading dataframe in v1 and csv in v2
            obj.upload_dataset_from_file = (
                compat_client.upload_dataset
            )  # currently only supports csv
            obj.upload_dataset_from_dir = compat_client.upload_dataset_from_dir
            # obj.process_csv = client_v1.process_csv
            # obj.process_avro = client_v1.process_avro

            obj.publish_event = compat_client.publish_event
            obj.publish_events_batch = compat_client.publish_events_batch
            # obj.publish_events_log = client_v1.publish_events_log #deprecated so not implemented
            obj.publish_events_batch_schema = compat_client.publish_events_batch_schema
            # obj.publish_parquet_s3 = client_v1.publish_parquet_s3
            obj.generate_sample_events = client_v1.generate_sample_events

            obj.upload_model_package = functools.partial(
                functools.partial(v1_upload_model_package, v1_client=client_v1),
                v2_client=client_v2,
            )
            obj.upload_model_package.__doc__ = client_v1.upload_model_package.__doc__

            obj.trigger_pre_computation = client_v1.trigger_pre_computation

            obj.register_model = functools.partial(
                functools.partial(v1_register_model, v1_client=client_v1),
                v2_client=client_v2,
            )
            obj.register_model.__doc__ = client_v1.register_model.__doc__

            obj.update_model = client_v1.update_model

            obj.add_model = functools.partial(
                functools.partial(add_model, v1_client=client_v1),
                v2_client=client_v2,
            )
            obj.add_model.__doc__ = add_model.__doc__

            obj.add_model_surrogate = functools.partial(
                functools.partial(add_model_surrogate, v1_client=client_v1),
            )
            obj.add_model_surrogate.__doc__ = add_model_surrogate.__doc__

            obj.add_model_artifact = functools.partial(
                functools.partial(add_model_artifact, v1_client=client_v1),
            )
            obj.add_model_artifact.__doc__ = add_model_artifact.__doc__ 

            obj._trigger_model_predictions = client_v1._trigger_model_predictions

            # explictly binding non-conflicting v1 methods to the v2 obj
            # conflicting methods will use v2 method by default for this condition
            # obj.project = client_v1.project

            obj.list_models = client_v1.list_models
            obj.get_model_info = client_v1.get_model_info
            obj.delete_model = client_v1.delete_model

            obj.get_slice = client_v1.get_slice

            obj.run_model = client_v1.run_model
            obj.run_explanation = client_v1.run_explanation
            obj.run_feature_importance = client_v1.run_feature_importance
            obj.run_fairness = client_v1.run_fairness
            obj.get_mutual_information = client_v1.get_mutual_information

            # The below methods are not used so not mapping them.
            # obj.share_project = client_v1.share_project
            # obj.unshare_project = client_v1.unshare_project
            # obj.list_org_roles = client_v1.list_org_roles
            # obj.list_project_roles = client_v1.list_project_roles
            # obj.list_teams = client_v1.list_teams

            # @todo make this available under client.v2
            # obj.initialize_monitoring = functools.partial(
            #     obj._initialize_monitoring, v1_connection=client_v1.connection
            # )

            # obj.add_monitoring_config = client_v1.add_monitoring_config
            # obj.list_segments = client_v1.list_segments
            # obj.upload_segment = client_v1.upload_segment
            # obj.activate_segment = client_v1.activate_segment
            # obj.deactivate_segment = client_v1.deactivate_segment
            # obj.delete_segment = client_v1.delete_segment
            # obj.get_segment_info = client_v1.get_segment_info
            # also retaining the sub-module approach
        else:
            logger.info('Default client is of client version 1')
            obj = client_v1
            if ServerDeploymentMode.F2 == server_deployment_mode:
                obj.publish_event = compat_client.publish_event
                obj.publish_events_batch = compat_client.publish_events_batch
                obj.publish_events_batch_schema = compat_client.publish_events_batch_schema

        obj.v1 = client_v1
        obj.v2 = client_v2
        return obj

    def _get_connection_parameters(
        self, url: str, org_id: str, auth_token: str, version: int
    ) -> Tuple:
        if Path('fiddler.ini').is_file():
            config = configparser.ConfigParser()
            config.read('fiddler.ini')
            info = config['FIDDLER']
            if not url:
                url = info.get('url', None)
            if not org_id:
                org_id = info.get('org_id', None)
            if not auth_token:
                auth_token = info.get('auth_token', None)

        if not url:
            raise ValueError('Could not find url. Please enter a valid url')
        if not org_id:
            raise ValueError('Could not find org_id. Please enter a valid org_id')
        if not auth_token:
            raise ValueError(
                'Could not find auth_token. Please enter a valid auth_token'
            )
        if version not in VERSIONS:
            raise ValueError(
                f'version={version} not supported. Please enter a valid version. Supported versions={VERSIONS}'
            )

        return url, org_id, auth_token

    def _get_supported_features(self, client_v1: FiddlerApiV1, org_id: str) -> Dict:
        supported_features: Dict = None

        try:
            path: List['str'] = ['get_supported_features', org_id]
            supported_features = client_v1.connection.call(path, is_get_request=True)
        except Exception as e:
            logger.warning('Fetching supported features failed with error ' + e.msg)

        return supported_features

    def _get_server_deployment_mode(
        self, supported_features: Optional[Dict] = None
    ) -> ServerDeploymentMode:
        ret_val: ServerDeploymentMode = ServerDeploymentMode.F1

        if supported_features:
            ret_val = (
                ServerDeploymentMode.F2
                if supported_features.get('enable_fiddler_v2', False)
                else ServerDeploymentMode.F1
            )

        return ret_val


def v1_upload_model_package(
    artifact_path: Path,
    project_id: str,
    model_id: str,
    deployment_type: Optional[
        str
    ] = DeploymentType.PREDICTOR,  # model deployment type. One of {'predictor', 'executor'}
    image_uri: Optional[str] = None,  # image to be used for newly uploaded model
    namespace: Optional[str] = None,  # kubernetes namespace
    port: Optional[int] = 5100,  # port on which model is served
    replicas: Optional[int] = 1,  # number of replicas
    cpus: Optional[float] = 0.25,  # number of CPU cores
    memory: Optional[str] = '128m',  # amount of memory required.
    gpus: Optional[int] = 0,  # number of GPU cores
    await_deployment: Optional[bool] = True,  # wait for deployment
    is_sync=True,
    v2_client: FiddlerApiV2 = None,
    v1_client: FiddlerApiV1 = None,
):
    v1_client.upload_model_package(
        artifact_path,
        project_id,
        model_id,
        deployment_type,
        image_uri,
        namespace,
        port,
        replicas,
        cpus,
        memory,
        gpus,
        await_deployment,
    )

    call_init_monitoring(v1_client, v2_client, project_id, model_id, is_sync)


def v1_register_model(
    project_id: str,
    model_id: str,
    dataset_id: str,
    model_info: ModelInfo,
    deployment: Optional[DeploymentOptions] = None,
    cache_global_impact_importance: bool = True,
    cache_global_pdps: bool = False,
    cache_dataset: bool = True,
    is_sync=True,
    v2_client: FiddlerApiV2 = None,
    v1_client: FiddlerApiV1 = None,
):
    v1_client.register_model(
        project_id,
        model_id,
        dataset_id,
        model_info,
        deployment,
        cache_global_impact_importance,
        cache_global_pdps,
        cache_dataset,
    )
    call_init_monitoring(v1_client, v2_client, project_id, model_id, is_sync)


def add_model(
    project_id: str,
    model_id: str,
    dataset_id: str = None,
    model_info: ModelInfo = None,
    is_sync: Optional[bool] = True,
    v2_client: FiddlerApiV2 = None,
    v1_client: FiddlerApiV1 = None,
) -> None:
    """
    Function to add a model to fiddler for monitoring

    :param project_id: project name where the model will be added
    :type project_id: string
    :param model_id: name of the model
    :type model_id: string
    :param dataset_id: name of the dataset
    :type dataset_id: string
    :param model_info: model related information from user
    :type model_info: ModelInfo
    :param is_sync: perform add model synchronously
    :type is_sync: boolean
    """
    if model_info is None:
        raise ValueError('ModelInfo cannot be None')
    if len(model_info.datasets) != 1:
        raise ValueError('Specify a single dataset for the model')

    if dataset_id and dataset_id in model_info.datasets:
        dataset_name = dataset_id
    else:
        dataset_name = model_info.datasets[0]

    dataset = v2_client.get_dataset(
        project_name=project_id, dataset_name=dataset_name
    )
    outputs = model_info.get_output_names()
    dataset_cols = set([col.name for col in dataset.info.columns])

    if not all(elem in dataset_cols for elem in outputs):
        raise ValueError(f'Dataset {dataset_name} does not have output columns')

    info = model_info.to_dict()
    model = v2_client.add_model(
        project_id, model_id, info, requirements='', framework=''
    )
    call_init_monitoring(v1_client, v2_client, project_id, model_id, is_sync)
    logger.info(f'Successfully added model {model.name} to project {project_id}')

def add_model_surrogate(
    project_id : str,
    model_id : str,
    v1_client: FiddlerApiV1 = None,
) -> None:
    """
    Trigger generation of surrogate model

    :param project_id: project name where the model will be added
    :type project_id: string
    :param model_id: name of the model
    :type model_id: string
    """

    model_info = (
        Project(v1_client.connection, project_id)
        .model(model_id)
        .get_info()
    )

    if model_info.artifact_status and model_info.artifact_status.value != ArtifactStatus.NO_MODEL.value:
        raise ValueError(f'Model {model_id} in project {project_id} already has artifact associated with it')

    dataset_name = model_info.datasets[0]
    model_info.artifact_status = ArtifactStatus.SURROGATE
    v1_client.register_model(project_id, model_id, dataset_name, model_info)

def add_model_artifact(
    project_id : str,
    model_id : str,
    model_dir : str,
    v1_client: FiddlerApiV1 = None,
) -> None:
    """
    Upload a user model artifact to the specified model, with model binary and package.py from
    the specified model_dir

    Note: changes to model.yaml is not supported right now.

    :param project_id: project id
    :type project_id: string
    :param model_id: model id
    :type model_id: string
    :param model_dir: model directory
    :type model_dir: string
    """
    v1_client.update_model(project_id=project_id, model_id=model_id, model_dir=model_dir, force_pre_compute=True)

def call_init_monitoring(
    v1_client: FiddlerApiV1,
    v2_client: FiddlerApiV2,
    project_id: str,
    model_id: str,
    is_sync: bool,
):

    logger.info('Start initialize monitoring')
    print('Start initialize monitoring')
    resp = Monitoring(v1_client.connection, project_id, model_id).initialize_monitoring(
        False, False, 'fiddler2'
    )

    if resp and is_sync:
        job_resp_final = v2_client.poll_job(resp)
        if job_resp_final.status == JobStatus.FAILURE:
            err_msg = 'Init monitoring failed with error message'
            logger.error(err_msg)
            raise Exception(f'{err_msg} - {job_resp_final.error_message}')
        elif job_resp_final.status == JobStatus.SUCCESS:
            results = FiddlerApiV2.get_task_results(job_resp_final)
            result_msg = '\n'.join(results)
            success_msg = f'Init monitoring succeeded:{result_msg}'
            logger.info(success_msg)
            print(success_msg)
            return True

        logger.info('Finished initialize monitoring')
        print('Finished initialize monitoring')

    else:
        return resp


__all__ = [
    '__version__',
    'BatchPublishType',
    'Column',
    'CustomFeature',
    'ColorLogger',
    'DatasetInfo',
    'DataType',
    'Fiddler',
    'FiddlerApi',
    'FiddlerTimestamp',
    'FiddlerPublishSchema',
    'gem',
    'MLFlowParams',
    'ModelDeploymentParams',
    'ModelInfo',
    'ModelInputType',
    'ModelTask',
    'ExplanationMethod',
    'PredictionEventBundle',
    'PackageValidator',
    'ValidationChainSettings',
    'ValidationModule',
    'utils',
    # Exposing constants
    'CSV_EXTENSION',
    'PARQUET_EXTENSION',
    'PARQUET_ROW_GROUP_SIZE',
    'PARQUET_ENGINE',
    'PARQUET_COMPRESSION',
]
