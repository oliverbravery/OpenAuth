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
    
    def dict(self, *args, **kwargs) -> dict:
        """
        Returns the dictionary representation of the Response object.

        Returns:
            dict: Dictionary representation of the Response object.
        """
        return {
            "status": self.status.value,
            "message": self.message
        }