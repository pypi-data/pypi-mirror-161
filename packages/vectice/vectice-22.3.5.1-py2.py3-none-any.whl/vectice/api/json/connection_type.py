from enum import Enum


class ConnectionType(Enum):
    """
    Enumeration of supported connection types.
    """

    GoogleBigQuery = "GoogleBigQuery"
    """
    """

    GoogleStorage = "GoogleStorage"
    """
    """

    GitHub = "GitHub"
    """
    """

    AmazonS3 = "AmazonS3"
    """
    """

    AmazonRedShift = "AmazonRedShift"
    """
    """

    Local = "Local"
    """
    """
