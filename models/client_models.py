from enum import Enum
from typing import List

from pydantic import BaseModel


class DeveloperScope(str, Enum):
    """
    Enum class for the different developer scopes
    """
    READ_PROFILE = "read:profile"
    WRITE_PROFILE = "write:profile"
    DELETE_PROFILE = "delete:profile"
    READ_CLIENT = "read:client"
    WRITE_CLIENT = "write:client"
    DELETE_CLIENT = "delete:client"

class ClientDeveloper(BaseModel):
    """
    Represents what scopes a developer has access to for a client.
    
    Args:
        username (str): The unique username of the developer.
        scopes (List[DeveloperScope]): The scopes that the developer has access to for the client.
    """
    username: str
    scopes: List[DeveloperScope]
    
class ScopeAccessType(str, Enum):
    """
    Represents all attribute access types.
    
    An attribute can be read, written, or both. It is used to determine what the client can do with the attribute.
    """
    READ = "read"
    WRITE = "write"
    READ_WRITE = "read_write"
    
class ScopeAttribute(BaseModel):
    """
    Represents an attribute in a scope and what the client can do with it.
    
    Args:
        name (str): The name of the attribute.
        access_type (ScopeAccessType): The access type of the attribute.
    """
    name: str
    access_type: ScopeAccessType
    
class ClientScope(BaseModel):
    """
    Represents a scope for a client.
    
    A scope is a permission that the client can request to allow it to access certain attributes of the user's profile.
    
    Args:
        name (str): The 'name' of the scope.
        description (str): A description of the scope and what it allows the client to do.
        shareable (bool): Whether other clients can request access to this scope.
        
    """
    name: str
    description: str
    shareable: bool
    attributes: List[ScopeAttribute]
    
class MetadataType(Enum):
    """
    Represents the possible types for a metadata attribute.
    """
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    
class MetadataAttribute(BaseModel):
    """
    Represents a metadata attribute for a client.
    
    Args:
        name (str): The name of the metadata attribute.
        description (str): The description of the metadata attribute.
        type (MetadataType): The type of the metadata attribute.
    """
    name: str
    description: str
    type: MetadataType

class Client(BaseModel):
    """
    Represents a registered application in the auth service. 
    A client is an application that can request access to a user's account and store application-specific data in the user's profile.
    
    Args:
        client_id (str): The unique attribute used to identify and differentiate applications.
        client_secret (str): A long random string that is used to authenticate the application.
        name (str): The name of the application.
        description (str): A description of the application and why it needs access to certain scopes.
        redirect_uri (str): The URI to which the user is redirected after granting or denying access to the application.
        developers (List[ClientAdmin]): The list of developers that have access to the client.
        scopes (list[ClientScope]): The scopes of the client.
        profile_metadata_attributes (List[MetadataAttribute]): The metadata attributes that the client can store in the user's profile.
        profile_defaults (dict[str, any]): Any default values that the client wants to store in the user's profile.
    """
    client_id: str
    client_secret: str
    name: str
    description: str
    redirect_uri: str
    developers: List[ClientDeveloper] = []
    scopes: list[ClientScope] = []
    profile_metadata_attributes: list[MetadataAttribute] = []
    profile_defaults: dict[str, any] = {}
    
    def get_profile_default(self, key: str) -> any:
        """
        Get the default value for the given key.

        Args:
            key (str): The key of the default value.

        Returns:
            any: The default value for the given key. None if the key does not exist.
        """
        return self.profile_defaults.get(key, None)