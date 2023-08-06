import json
from typing import Any
from urllib.parse import urljoin

import requests

from .abstract_service_connexion import AbstractServiceConnexion
from .exceptions import NetworkError, UnauthorizedError


class JwtServiceConnexion(AbstractServiceConnexion):
    def __init__(
        self,
        host: str,
        jwt_identifier_data: dict,
        authorization_key: str = "Bearer",
        login_path: str = "/login",
    ) -> None:
        """JwtServiceConnexion may be use to handle a JwtAuthentication connexion with a service.
        You need to give a jwt_identifier_data (as a dict) that will be send to the host to ensures validity of your request.
        This data will depend on service contacted. For example for a Deployment / Jwt request on Oracle, this will be :
        {
            "api_token" : <user_api_token>,
            "deployment_id" : <deployment_id>
        }
        """
        self.jwt_identifier_data = jwt_identifier_data
        self.login_path = login_path
        self.authorization_key = authorization_key
        self.host = host
        self.jwt, self.expires_in = self.generate_jwt()

    def wrapped_request(f):
        def decorated(self, *args, regenerate_jwt=True, **kwargs):
            try:
                resp = f(self, *args, **kwargs)
            except Exception:
                raise NetworkError("Server is not responding, please check your host.")

            if resp.status_code == 401:
                res = resp.json()
                if regenerate_jwt and "expired" in res and res["expired"]:
                    self.jwt, self.expires_in = self.generate_jwt()
                    return decorated(self, *args, regenerate_jwt=False, **kwargs)
                else:
                    raise UnauthorizedError("You are not authorized to do this.")

            return resp

        return decorated

    def generate_jwt(self):
        url = urljoin(self.host, self.login_path)
        try:
            response = requests.post(url=url, data=json.dumps(self.jwt_identifier_data))
        except Exception:
            raise NetworkError("Server is not responding, please check your host.")

        if response.status_code == 200:
            try:
                data = response.json()
                return data["jwt"], data["expires"]
            except Exception:
                raise UnauthorizedError(
                    "Cannot parse response from external service. Please contact support."
                )
        else:
            raise UnauthorizedError("Unauthorized action on the deployment services")

    def _build_headers(self):
        return {"Authorization": "{} {}".format(self.authorization_key, self.jwt)}

    @wrapped_request
    def get(self, path: str, params: dict = None, stream=False):
        url = urljoin(self.host, path)
        return requests.get(
            url=url,
            headers=self._build_headers(),
            params=params,
            stream=stream,
        )

    @wrapped_request
    def xget(self, path: str, data: dict = None, params: dict = None, stream=False):
        url = urljoin(self.host, path)
        return requests.api.request(
            method="XGET",
            url=url,
            data=data,
            headers=self._build_headers(),
            params=params,
            stream=stream,
        )

    @wrapped_request
    def post(
        self, path: str, data: dict = None, params: dict = None, files: Any = None
    ):
        url = urljoin(self.host, path)
        return requests.post(
            url=url,
            data=data,
            headers=self._build_headers(),
            params=params,
            files=files,
        )

    @wrapped_request
    def patch(self, path: str, data: dict = None, params: dict = None):
        url = urljoin(self.host, path)
        return requests.patch(
            url=url, data=data, headers=self._build_headers(), params=params
        )

    @wrapped_request
    def put(self, path: str, data: dict = None, params: dict = None):
        url = urljoin(self.host, path)
        return requests.put(
            url=url, data=data, headers=self._build_headers(), params=params
        )

    @wrapped_request
    def delete(self, path: str, data: dict = None, params: dict = None):
        url = urljoin(self.host, path)
        return requests.delete(
            url=url, data=data, headers=self._build_headers(), params=params
        )
