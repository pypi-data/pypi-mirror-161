from http import HTTPStatus
from typing import List, Optional

from pydantic import parse_obj_as

from fiddler.libs.http_client import RequestClient
from fiddler.utils import logging
from fiddler.v2.schema.model import Model
from fiddler.v2.utils.exceptions import handle_api_error_response
from fiddler.v2.utils.response_handler import (
    APIResponseHandler,
    PaginatedResponseHandler,
)

logger = logging.getLogger(__name__)


class ModelMixin:
    client: RequestClient
    organization_name: str

    @handle_api_error_response
    def get_models(self, project_name: str) -> List[Model]:
        """
        Get list of all models belonging to a project

        :params project_name: The project for which you want to get the models
        :returns: List containing Model objects
        """
        response = self.client.get(
            url='models',
            params={
                'organization_name': self.organization_name,
                'project_name': project_name,
            },
        )
        _, items = PaginatedResponseHandler(response).get_pagination_details_and_items()
        return parse_obj_as(List[Model], items)

    @handle_api_error_response
    def get_model(self, project_name: str, model_name: str) -> Model:
        """
        Get the details of a model.

        :params project_name: The project to which the model belongs to
        :params model_name: The model name of which you need the details
        :returns: Model object which contains the details
        """
        response = self.client.get(
            url=f'models/{self.organization_name}:{project_name}:{model_name}',
        )
        response_handler = APIResponseHandler(response)
        return Model.deserialize(response_handler)

    @handle_api_error_response
    def add_model(
        self,
        project_name: str,
        model_name: str,
        info: Optional[dict] = None,
        model_type: Optional[str] = None,
        framework: Optional[str] = None,
        requirements: Optional[str] = None,
    ) -> Model:
        """
        Function to add a model to fiddler for monitoring

        :param project_name: project name where the model will be added
        :type project_name: string
        :param model_name: name of the model
        :type model_name: string
        :param info: model related information passed as dictionary from user
        :type info: dictionary
        :param model_type: the type of model e.g. REGRESSION, BINARY CLASSIFICATION
        :type model_type: string
        :return: Model object which contains the model details
        """
        # @TODO: file_list required while setting up model?
        # @TODO: Handle model_deployment_id?
        request_body = Model(
            organization_name=self.organization_name,
            project_name=project_name,
            name=model_name,
            info=info,
            model_type=model_type,
            framework=framework,
            requirements=requirements,
        ).dict()

        # remove id key from POST request, as it will be created by the backend
        if 'id' in request_body:
            request_body.pop('id')

        response = self.client.post(
            url='models',
            data=request_body,
        )
        logger.info(f'{model_name} setup successful')

        return Model.deserialize(APIResponseHandler(response))

    @handle_api_error_response
    def delete_model(self, project_name: str, model_name: str) -> None:
        """
        Delete a model

        :params project_name: Project name to which the model belongs to.
        :params model_name: Model name to be deleted

        :returns: None
        """
        response = self.client.delete(
            url=f'models/{self.organization_name}:{project_name}:{model_name}',
        )
        if response.status_code == HTTPStatus.OK:
            logger.info(f'{model_name} delete request received.')
        else:
            # @TODO: Handle non 200 status response
            logger.info('Delete unsuccessful')
