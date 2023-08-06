from typing import Any
from urllib.parse import urljoin

import requests

from .abstract_service_connexion import AbstractServiceConnexion
from .exceptions import NetworkError


class TokenServiceConnexion(AbstractServiceConnexion):
    def __init__(
        self,
        host: str,
        api_token: str,
        authorization_key: str = "Token",
        content_type: str = "application/json",
    ) -> None:
        """TokenServiceConnexion may be use to handle a Token authentication connexion with a service.
        You need to give an api token valid, recognized by the service called
        """
        self.host = host
        self.api_token = api_token
        self.headers = {
            "Authorization": authorization_key + " " + api_token,
            "Content-type": content_type,
        }

    def wrapped_request(f):
        def decorated(*args, **kwargs):
            try:
                resp = f(*args, **kwargs)
            except Exception:
                raise NetworkError("Server is not responding, please check your host.")
            return resp

        return decorated

    def add_header(self, key: str, value: str):
        assert (
            key is not None and value is not None
        ), "Header key and value can't be None"
        self.headers[key] = value

    @wrapped_request
    def get(self, path: str, params: dict = None, stream=False):
        url = urljoin(self.host, path)
        return requests.get(url=url, headers=self.headers, params=params, stream=stream)

    @wrapped_request
    def xget(self, path: str, data: dict = None, params: dict = None, stream=False):
        url = urljoin(self.host, path)
        return requests.api.request(
            method="XGET",
            url=url,
            data=data,
            headers=self.headers,
            params=params,
            stream=stream,
        )

    @wrapped_request
    def post(
        self, path: str, data: dict = None, params: dict = None, files: Any = None
    ):
        url = urljoin(self.host, path)
        return requests.post(
            url=url, data=data, headers=self.headers, params=params, files=files
        )

    @wrapped_request
    def patch(self, path: str, data: dict = None, params: dict = None):
        url = urljoin(self.host, path)
        return requests.patch(url=url, data=data, headers=self.headers, params=params)

    @wrapped_request
    def put(self, path: str, data: dict = None, params: dict = None):
        url = urljoin(self.host, path)
        return requests.put(url=url, data=data, headers=self.headers, params=params)

    @wrapped_request
    def delete(self, path: str, data: dict = None, params: dict = None):
        url = urljoin(self.host, path)
        return requests.delete(url=url, data=data, headers=self.headers, params=params)
