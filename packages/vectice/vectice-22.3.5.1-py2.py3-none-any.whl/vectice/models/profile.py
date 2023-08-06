from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from vectice import Reference


class Profile:
    """
    User Profile information
    """

    def __init__(self, login: str, default_workspace: Optional[Reference] = None):
        self._login = login
        self._default_workspace = default_workspace

    """
    user login/email

    """

    @property
    def login(self) -> str:
        return self._login

    """
    default workspace is no workspace is given in the API.

    """

    @property
    def default_workspace(self) -> Optional[Reference]:
        return self._default_workspace
