from typing import Union, Any, Optional

from vectice.api._http import HttpError

Reference = Union[str, int]


class InvalidReferenceError(ValueError):
    def __init__(self, reference_type: str, value: Any) -> None:
        super().__init__(
            f"The {reference_type} reference is invalid. Please check the provided value. "
            + "it should be a string or a number. "
            + f"Provided value is {value} ({type(value)})"
        )


class BadReferenceError(ValueError):
    def __init__(self, reference_type: str, value: Reference, error: HttpError) -> None:
        if isinstance(value, str):
            super().__init__(
                # f"{error.method.upper()} {error.path}: HTTP CODE {error.code}\n"
                f"The reference does not reference any known {reference_type} . Please check the provided value. "
                + f"{reference_type} named '{value}' is unknown"
            )
        else:
            super().__init__(
                f"The reference does not reference any known {reference_type} . Please check the provided value. "
                + f"{reference_type} with identifier <{value}> is unknown"
            )


class MissingReferenceError(ValueError):
    def __init__(self, reference_type: str, parent_reference_type: Optional[str] = None) -> None:
        if parent_reference_type is not None:
            super().__init__(f"the {parent_reference_type} reference is required if the {reference_type} name is given")
        else:
            super().__init__(f"the {reference_type} reference is required")
