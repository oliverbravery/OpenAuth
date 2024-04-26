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
    Represents an attribute of a profile (and it's metadata) and what a scope can do with it.
    
    Args:
        attribute_name (str): The name of the attribute in the profile/ profile metadata.
        access_type (ScopeAccessType): The access type of the attribute.
    """
    attribute_name: str
    access_type: ScopeAccessType
    
class ClientScope(BaseModel):
    """
    Represents a scope for a client.
    
    A scope is a permission that the client can request to allow it to access certain attributes of the user's profile.
    
    Args:
        name (str): The 'name' of the scope.
        description (str): A description of the scope and what it allows the client to do.
        shareable (bool): Whether other clients can request access to this scope.
        associated_attributes (List[ScopeAttribute]): The attributes (profile or profile metadata) that this scope controls.
    """
    name: str
    description: str
    shareable: bool
    associated_attributes: List[ScopeAttribute]

class ProfileScope(BaseModel):
    """
    Represents a scope in a profile for an app.
    
    Defines for a specific application what scopes the user has granted access to.
    
    Args:
        client_id (str): The client the scope is associated with.
        scope (str): The scope that the application is allowed to access.
    """
    client_id: str
    scope: str
    