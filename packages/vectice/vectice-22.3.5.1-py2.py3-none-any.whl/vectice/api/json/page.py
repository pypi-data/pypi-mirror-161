from dataclasses import dataclass


@dataclass
class Page:
    """
    simple structure to allow paging when requesting list of elements
    """

    index: int = 1
    """
    the index of the page
    """
    size: int = 100
    """
    the size of the page.
    """
