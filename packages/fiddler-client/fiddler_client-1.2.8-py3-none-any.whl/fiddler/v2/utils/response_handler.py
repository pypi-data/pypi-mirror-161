from typing import Dict, List, Tuple

try:
    from simplejson import JSONDecodeError
except ImportError:
    from json import JSONDecodeError

import requests

from fiddler.utils import logging
from fiddler.v2.utils.exceptions import FiddlerAPIException

logger = logging.getLogger(__name__)


class BaseResponseHandler:
    def __init__(self, response: requests.Response) -> None:
        self.response = response
        logger.debug(self.response.content)

    def get_data(self) -> Dict[str, dict]:
        try:
            dict_response = self.response.json().get('data')
        except JSONDecodeError:
            raise FiddlerAPIException(
                status_code=self.response.status_code,
                error_code=self.response.status_code,
                message=f'Invalid response content-type. {self.response.status_code}:{self.response.content}',
                errors=[],
            )
        dict_response.pop('created_at', None)
        dict_response.pop('updated_at', None)
        return dict_response

    def get_status_code(self) -> int:
        return self.response.status_code


class PaginatedResponseHandler(BaseResponseHandler):
    '''
    Handle fiddler OAS's standard Paginated response
    '''

    def get_pagination_details_and_items(self) -> Tuple[dict, List[dict]]:
        data = self.get_data()
        items = data.pop('items')
        return data, items


class APIResponseHandler(BaseResponseHandler):
    '''
    Handle fiddler OAS's standard API Response
    '''


class JobResponseHandler(BaseResponseHandler):
    def __init__(self, response: requests.Response) -> None:
        super().__init__(response)
        data = self.get_data()
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.status = data.get('status')
        self.progress = data.get('progress')
        self.error_message = data.get('error_message')
        self.extras = data.get('extras')
