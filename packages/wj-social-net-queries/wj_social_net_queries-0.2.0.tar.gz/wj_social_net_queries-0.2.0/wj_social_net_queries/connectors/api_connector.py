import json
from typing import Optional

import requests

from ..utils.constants.constants import DELETE, GET, PATCH, POST


class ApiConnector:
    api_url = None

    def __init__(self) -> None:
        pass

    def api_request(
        self,
        request_url: str,
        operation: str,
        data: Optional[dict] = {},
        params: Optional[dict] = {},
        headers: Optional[dict] = {},
    ) -> dict:
        """
        Description
        ----------
            Makes the requets to API url.
        """
        try:
            if operation == GET:
                response = requests.get(
                    request_url, data=json.dumps(data), params=params, headers=headers
                )
            elif operation == POST:
                response = requests.post(
                    request_url, data=json.dumps(data), params=params, headers=headers
                )
            elif operation == PATCH:
                response = requests.patch(
                    request_url, data=json.dumps(data), params=params, headers=headers
                )
            elif operation == DELETE:
                response = requests.delete(
                    request_url, data=json.dumps(data), params=params, headers=headers
                )

        except requests.exceptions.ConnectionError:
            response = requests.models.Response()
            response.status_code = 502

        return response
