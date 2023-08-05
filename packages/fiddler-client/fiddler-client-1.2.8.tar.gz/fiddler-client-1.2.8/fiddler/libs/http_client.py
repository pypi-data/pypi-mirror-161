import json
from copy import deepcopy
from typing import Dict, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter

APP_JSON_CONTENT_TYPE = 'application/json'


class RequestClient:
    def __init__(self, base_url: str, headers: Dict[str, str]) -> None:
        self.base_url = base_url
        self.headers = headers
        self.headers.update({'Content-Type': APP_JSON_CONTENT_TYPE})
        self.session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=25,
            pool_maxsize=25,
        )
        self.session.mount(self.base_url, adapter)

    def call(
        self,
        *,
        method: str,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Make request to server
        """
        full_url = urljoin(self.base_url + '/', url)

        request_headers = self.headers
        # override/update headers coming from the calling method
        if headers:
            request_headers = deepcopy(self.headers)
            request_headers.update(headers)

        content_type = request_headers.get('Content-Type')
        if content_type == APP_JSON_CONTENT_TYPE:
            data = json.dumps(data)
        response = self.session.request(
            method,
            full_url,
            params=params,
            data=data,
            headers=request_headers,
            timeout=timeout,
            **kwargs,
        )
        response.raise_for_status()
        return response

    def get(
        self,
        *,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ):
        return self.call(
            method='GET',
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def delete(
        self,
        *,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: Optional[int] = None,
        **kwargs,
    ):
        return self.call(
            method='DELETE',
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    def post(
        self,
        *,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: Optional[int] = None,
        data: Optional[dict] = None,
        **kwargs,
    ):
        return self.call(
            method='POST',
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            data=data,
            **kwargs,
        )

    def put(
        self,
        *,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: Optional[int] = None,
        data: Optional[dict] = None,
        **kwargs,
    ):
        return self.call(
            method='PUT',
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            data=data,
            **kwargs,
        )

    def patch(
        self,
        *,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: Optional[int] = None,
        data: Optional[dict] = None,
        **kwargs,
    ):
        return self.call(
            method='PATCH',
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            data=data,
            **kwargs,
        )
