import json
import logging
import os
from base64 import b64decode
from datetime import datetime
from typing import Optional

from ._http import Connection
from ._utils import read_env


class Auth(Connection):  # nosec B107
    def __init__(
        self,
        api_endpoint: str = None,
        api_token: str = None,
        token: Optional[str] = None,
        auto_connect=True,
        allow_self_certificate=True,
    ):
        self._logger = logging.getLogger("vectice.auth")
        self._API_TOKEN = None
        endpoint_env, endpoint = None, None
        if api_endpoint is not None:
            endpoint = api_endpoint
        else:
            endpoint_env = read_env("VECTICE_API_ENDPOINT")[0]
        if api_token is not None:
            self._API_TOKEN = api_token
        else:
            env_value = read_env("VECTICE_API_TOKEN")[0]
            if env_value is not None:
                self._API_TOKEN = env_value
        if endpoint_env is not None:
            endpoint = endpoint_env
        if not endpoint:
            raise ValueError("VECTICE_API_ENDPOINT is not provided.")
        if not self._API_TOKEN:
            raise ValueError("VECTICE_API_TOKEN is not provided.")
        super().__init__(api_endpoint=endpoint, allow_self_certificate=allow_self_certificate)
        self._jwt = None
        self._jwt_expiration = None
        if token:
            self._token = token
        elif auto_connect:
            self._refresh_token()
        self.vectice_path: Optional[str] = None

    @property
    def _token(self) -> Optional[str]:
        if self._jwt_expiration is None:
            return None
        # Refresh token 1 min before expiration
        if datetime.now().timestamp() >= self._jwt_expiration - 60:
            self._refresh_token()
        return self._jwt

    @_token.setter
    def _token(self, jwt: str) -> None:
        self._jwt = jwt
        self._jwt_expiration = self._get_jwt_expiration(jwt)
        self._default_request_headers["Authorization"] = "Bearer " + jwt

    def _refresh_token(self) -> None:
        self._logger.debug("Vectice: Refreshing token... ")
        response = self._post("/metadata/authenticate", {"apiKey": self._API_TOKEN})
        self._token = response["token"]
        self._logger.debug("Success!")

    @staticmethod
    def auth_api_token(api_token: str, api_endpoint: Optional[str]):
        logging.info("Vectice: Validating api token... ")
        if api_endpoint is None and os.getenv("VECTICE_API_ENDPOINT"):
            api_endpoint = os.getenv("VECTICE_API_ENDPOINT")
        elif api_endpoint is None and not os.getenv("VECTICE_API_ENDPOINT"):
            raise ValueError("No api endpoint could be found to connect to the Vectice App!")
        try:
            Connection(api_endpoint)._post("/metadata/authenticate", {"apiKey": api_token})
        except Exception as e:
            raise RuntimeError(f"Could not authenticate due to: {e}")
        logging.info("Success!")

    @staticmethod
    def _get_jwt_expiration(jwt: str) -> int:
        jwt_payload = jwt.split(".")[1]
        jwt_payload_with_padding = f"{jwt_payload}{'=' * (4 - len(jwt_payload) % 4)}"
        return int(json.loads(b64decode(jwt_payload_with_padding))["exp"])

    def token(self) -> Optional[str]:
        return self._token

    def connect(self) -> None:
        self._refresh_token()
