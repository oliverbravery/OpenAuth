from pydantic import BaseModel
from enum import Enum

class ResponseStatus(Enum):
    """
    ResponseStatus Enum class for the response statuses.
    """
    SUCCESS = "success"
    ERROR = "error"
    
class Response(BaseModel):
    """
    Response model extending Pydantic's BaseModel class.
    Represents a response object with a status and message.
    
    Args:
        status (ResponseStatus): The status of the response.
        message (str): The message of the response.
    """
    status: ResponseStatus
    message: str