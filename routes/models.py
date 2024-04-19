from pydantic import BaseModel
from enum import Enum

class ResponseStatus(Enum):
    """
    ResponseStatus Enum class for the response statuses.
    """
    SUCCESS = "success"
    ERROR = "error"