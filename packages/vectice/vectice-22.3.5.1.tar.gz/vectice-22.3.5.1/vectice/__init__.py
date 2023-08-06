from . import models
from . import api
from .api import Reference
from .integrations import Integrations

from .vectice import Vectice
from vectice.experiment import Experiment
from .__version__ import __version__


_AUTOLOGGING = []

try:
    import mlflow.sklearn as sklearn
    import mlflow.tracking.fluent.autolog as autolog

    _AUTOLOGGING = ["autolog", "sklearn"]

except ImportError:
    pass

version = __version__

__all__ = ["Vectice", "api", "Integrations", "models", "Experiment", "version"] + _AUTOLOGGING
