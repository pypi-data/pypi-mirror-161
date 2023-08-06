from vectice.api._auth import Auth
from vectice.api.http_error_handlers import HttpErrorHandler
from vectice.api.json.compatibility import CompatibilityOutput


class CompatibilityApi:
    def __init__(self, auth: Auth):
        self._auth = auth
        self._httpErrorhandler = HttpErrorHandler()

    def check_version(self) -> CompatibilityOutput:
        response = self._auth._get("/metadata/compatibility")
        if "message" not in response.keys():
            return CompatibilityOutput(message="", status="OK")
        else:
            return CompatibilityOutput(**response)
