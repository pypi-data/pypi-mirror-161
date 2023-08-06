from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vectice.models import Run


class AbstractIntegration(ABC):
    @abstractmethod
    def lib_name(self) -> str:
        pass

    @abstractmethod
    def before_start(self, vectice_run: Run) -> None:
        """ """
        pass

    @abstractmethod
    def after_start(self, vectice_run: Run) -> None:
        """ """
        pass

    @abstractmethod
    def before_stop(self, vectice_run: Run) -> None:
        """ """
        pass

    @abstractmethod
    def after_stop(self, vectice_run: Run) -> None:
        """ """
        pass
