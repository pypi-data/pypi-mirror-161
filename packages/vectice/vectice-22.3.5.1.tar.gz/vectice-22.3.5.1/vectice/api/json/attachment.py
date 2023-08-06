from dataclasses import dataclass

from typing import Optional


@dataclass
class AttachmentOutput:
    fileId: int
    fileName: str
    contentType: str
    entityId: int
    entityType: str
    modelFramework: Optional[str] = None
