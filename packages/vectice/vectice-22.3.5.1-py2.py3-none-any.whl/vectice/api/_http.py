import logging
import os
import re
import textwrap
from enum import Enum
from json import JSONEncoder
from typing import Dict, Any, cast, Optional, List, Tuple, BinaryIO, Sequence

import requests
import urllib3
from requests import Response

from vectice.__version__ import __version__, __vectice_version__
from vectice.api.json_object import JsonObject

DEFAULT_API_ENDPOINT = "http://localhost:4000"

logger = logging.getLogger("vectice.http")


class HttpError(Exception):
    def __init__(self, code: int, reason: str, path: str, method: str, json: Optional[str]):
        super().__init__()
        self.code: int = code
        self.reason: str = reason
        self.path = path
        self.method = method
        self.json = json

    def __str__(self):
        begin = textwrap.dedent(
            f"""
            HTTP Error Code {self.code} : {self.reason}
            {self.method} {self.path}
        """
        )
        if self.json:
            end = textwrap.dedent(
                f"""
                ---- payload ---
                {self.json}
                ---
                """
            )
        else:
            end = ""
        return begin + end


def format_url(url: str) -> str:
    """Add https protocol if missing and remove trailing slash."""
    url = url.rstrip("/")
    if not re.match("(?:http|https|ftp)://", url):
        return "https://{}".format(url)
    return url


def log_request(method: str, path: str, headers: dict, payload: Optional[Any] = None) -> None:
    should_log = os.getenv("LOG_VECTICE_HTTP_REQUEST")
    if should_log is not None and should_log != "0" and should_log.lower() != "false":
        logger.info("###")
        logger.info(f"{method} {path}")
        for item in headers.items():
            logger.info(f"{item[0]}: {item[1] if item[0] != 'Authorization' else '********'}")
        logger.info(payload)
    else:
        logger.debug("###")
        logger.debug(f"{method} {path}")
        for item in headers.items():
            logger.debug(f"{item[0]}: {item[1] if item[0] != 'Authorization' else '********'}")
        logger.debug(payload)


def default_http_headers() -> Dict[str, str]:
    return {"Vectice-SDK-Version": __version__, "Vectice-Version": __vectice_version__}


class VecticeEncoder(JSONEncoder):
    """
    Json Encoder with 2 specific behaviors:
    - handle datetime types so be serialized as a string following ISO8601 format
    - remove any null property from the serialized json.
    - handle nested objects
    """

    def default(self, obj: Any) -> Any:
        from copy import deepcopy

        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        internal_copy = deepcopy(obj.__dict__)
        return {k.lstrip("_"): v for (k, v) in internal_copy.items() if v is not None}


class Connection:
    def __init__(self, api_endpoint: Optional[str] = None, allow_self_certificate=True):
        self._API_BASE_URL = format_url(api_endpoint or DEFAULT_API_ENDPOINT)
        self._default_request_headers: Dict[str, str] = default_http_headers()
        self.verify_certificate = not allow_self_certificate
        if allow_self_certificate:
            urllib3.disable_warnings()

    @property
    def api_base_url(self) -> str:
        return self._API_BASE_URL

    def _clean_dict(self, payload: dict):
        cleaned_payload = {}
        for key, value in payload.items():
            if value is not None:
                if isinstance(value, Dict):
                    cleaned_payload[key] = self._clean_dict(value)
                else:
                    cleaned_payload[key] = value
        return cleaned_payload

    def _get(self, path: str) -> Dict[str, Any]:
        headers = {**self._default_request_headers, "Content-Type": "application/json"}
        log_request("GET", path, headers)
        response = requests.get(url=self.api_base_url + path, headers=headers, verify=self.verify_certificate)
        return self._response(self.api_base_url + path, headers, response, "GET")

    def _post(self, path: str, payload: Any = None) -> JsonObject:
        headers = {**self._default_request_headers, "Content-Type": "application/json"}
        cleaned_payload: Any = self._clean_dict(payload) if isinstance(payload, Dict) else payload
        data = VecticeEncoder(indent=1).encode(cleaned_payload)
        log_request("POST", path, headers, data)
        response = requests.post(
            url=self.api_base_url + path, headers=headers, data=data, verify=self.verify_certificate
        )
        return self._response(self.api_base_url + path, headers, response, "POST", data)

    def _put(self, path: str, payload: Any = None) -> JsonObject:
        headers = {**self._default_request_headers, "Content-Type": "application/json"}
        cleaned_payload: Any = self._clean_dict(payload) if isinstance(payload, Dict) else payload
        data = VecticeEncoder(indent=1).encode(cleaned_payload)
        log_request("PUT", path, headers, data)
        response = requests.put(
            url=self.api_base_url + path, headers=headers, data=data, verify=self.verify_certificate
        )
        return self._response(self.api_base_url + path, headers, response, "PUT", payload)

    def _delete(self, path: str, payload: Any = None) -> JsonObject:
        headers = {**self._default_request_headers, "Content-Type": "application/json"}
        if payload is None:
            data = None
        else:
            cleaned_payload: Any = self._clean_dict(payload) if isinstance(payload, Dict) else payload
            data = VecticeEncoder(indent=1).encode(cleaned_payload)
        log_request("DELETE", path, headers, data)
        response = requests.delete(
            url=self.api_base_url + path, headers=headers, data=data, verify=self.verify_certificate
        )
        return self._response(self.api_base_url + path, headers, response, "DELETE", data)

    def _post_attachments(
        self, path: str, files: Optional[Sequence[Tuple[str, Tuple[Any, BinaryIO]]]] = None
    ) -> Optional[Response]:
        headers = self._default_request_headers
        response = requests.post(
            url=self.api_base_url + path,
            headers=headers,
            files=files,  # type: ignore
            verify=self.verify_certificate,
        )
        return self._attachment_response(self.api_base_url + path, headers, response, "POST")

    def _put_attachments(
        self, path: str, files: Optional[List[Tuple[str, Tuple[Any, BinaryIO]]]] = None
    ) -> Optional[Response]:
        headers = self._default_request_headers
        response = requests.put(
            url=self.api_base_url + path,
            headers=headers,
            files=files,  # type: ignore
            verify=self.verify_certificate,
        )
        return self._attachment_response(self.api_base_url + path, headers, response, "PUT")

    def _get_attachment(self, path: str) -> Response:
        headers = self._default_request_headers
        response = requests.get(
            url=self.api_base_url + path, headers=headers, verify=self.verify_certificate, stream=True
        )
        return self._attachment_response(self.api_base_url + path, headers, response, "GET")

    def _delete_attachment(self, path: str) -> Optional[Response]:
        headers = self._default_request_headers
        response = requests.delete(url=self.api_base_url + path, headers=headers)
        return self._attachment_response(self.api_base_url + path, headers, response, "DELETE")

    def _list_attachments(self, path: str) -> Sequence[dict]:
        headers = {**self._default_request_headers, "Content-Type": "application/json"}
        response = requests.get(url=self.api_base_url + path, headers=headers, verify=self.verify_certificate)
        self._attachment_response(self.api_base_url + path, headers, response, "GET")
        return cast(Sequence[Dict], response.json())

    @classmethod
    def raise_status(cls, path: str, response: Response, method: str, payload: Optional[Any] = None) -> None:
        if not (200 <= response.status_code < 300):
            reason = response.text
            if not isinstance(payload, str):
                json = VecticeEncoder(indent=4, sort_keys=True).encode(payload) if payload is not None else None
            else:
                json = payload
            raise HttpError(response.status_code, reason, path, method, json)

    def _response(
        self, path: str, headers: Dict[str, str], response: Response, method: str, payload: Optional[Any] = None
    ) -> JsonObject:
        self.raise_status(path, response, method, payload)
        logger.debug(f"{method} {path} {response.status_code}")
        logger.debug("\n".join(f"{item[0]}: {item[1]}" for item in headers.items()))
        logger.debug(payload)
        if len(response.content) > 0:
            return cast(Dict[str, Any], response.json())
        return {response.reason: response.status_code}

    def _attachment_response(self, path: str, headers: Dict[str, str], response: Response, method: str) -> Response:
        self.raise_status(path, response, method)
        logger.debug(f"{method} {path} {response.status_code}")
        logger.debug("\n".join(f"{item[0]}: {item[1]}" for item in headers.items()))
        return response
