from dataclasses import dataclass
from typing import Optional, List


@dataclass
class User:
    """
    Defines the user entity inside Vectice
    """

    organizationId: int
    """
    """
    name: str
    """
    """
    email: str  # Do we need this in the SDK side
    """
    """
    password: str  # Do we need this in the SDK side
    """
    """
    token: str = ""
    """
    """
    workspaces: Optional[List[str]] = None
    """
    """
    requestId: Optional[str] = None
    """
    """
    inviteId: Optional[str] = None
    """
    """
    displayName: Optional[str] = None
    """
    """
