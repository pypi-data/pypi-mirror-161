from __future__ import annotations

from typing import TYPE_CHECKING

from ._http import HttpError
from .reference import BadReferenceError

if TYPE_CHECKING:
    from vectice import Reference


class HttpErrorHandler:
    def handleGetHttpError(self, e: HttpError, reference_type: str, reference: Reference) -> Exception:
        if e.code == 404:
            return BadReferenceError(reference_type, reference, e)
        elif e.code == 401:
            return PermissionError("bad or missing credentials")
        elif e.code == 403:
            return PermissionError(f"missing rights to access this {reference_type}")
        else:
            return RuntimeError(f"can not access {reference_type}: {e.reason}")

    def handlePostHttpError(self, e: HttpError, reference_type: str, action: str = "create") -> Exception:
        if e.code == 401:
            return PermissionError("bad or missing credentials")
        elif e.code == 403:
            return PermissionError(f"missing rights to access this {reference_type}")
        elif e.code == 400:
            return RuntimeError(f"can not {action} {reference_type}: {e.reason}")
        else:
            return RuntimeError(f"unexpected error: {e.reason}")

    def handlePutHttpError(self, e: HttpError, reference_type: str, reference: Reference) -> Exception:
        if e.code == 404:
            return BadReferenceError(reference_type, reference, e)
        elif e.code == 401:
            return PermissionError("bad or missing credentials")
        elif e.code == 403:
            return PermissionError(f"missing rights to access this {reference_type}")
        elif e.code == 400:
            return RuntimeError(f"can not update {reference_type} {reference}: {e.reason}")
        else:
            return RuntimeError(f"unexpected error: {e.reason}")

    def handleDeleteHttpError(self, e: HttpError, reference_type: str, reference: Reference) -> Exception:
        if e.code == 404:
            return BadReferenceError(reference_type, reference, e)
        elif e.code == 401:
            return PermissionError("bad or missing credentials")
        elif e.code == 403:
            return PermissionError(f"missing rights to access this {reference_type}")
        elif e.code == 400:
            return RuntimeError(f"can not delete {reference_type} {reference}: {e.reason}")
        else:
            return RuntimeError(f"unexpected error: {e.reason}")
