from enum import Enum


class ArtifactType(Enum):
    """
    Enumeration of supported artifact types.
    """

    MODEL = "MODEL"
    """
    """

    CODE = "CODE"
    """
    """

    DATASET = "DATASET"
    """
    """


class JobArtifactType(Enum):
    """
    Indicates whether the artifact is an input or an output of a run.
    """

    INPUT = "INPUT"
    """
    """
    OUTPUT = "OUTPUT"
    """
    """
