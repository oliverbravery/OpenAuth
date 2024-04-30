from enum import Enum
from typing import List
from pydantic import BaseModel

class AccountAttribute(str, Enum):
    """
    Enum class for representing the different attributes an account has (non-profile attributes)
    """
    DISPLAY_NAME = "display_name"
    EMAIL = "email"
    
class ScopeAccessType(str, Enum):
    """
    Represents all attribute access types.
    
    An attribute can be read, written, or both. It is used to determine what the client can do with the attribute.
    """
    READ = "read"
    WRITE = "write"
    
class ClientScopeAttribute(BaseModel):
    """
    Represents an attribute of the client's specific metadata and what a scope can do with it.
    
    NOTE: This is only for the client's metadata attributes.
    
    Args:
        attribute_name (str): The name of the attribute in the profile metadata.
        access_type (ScopeAccessType): The access type of the attribute.
    """
    attribute_name: str
    access_type: ScopeAccessType
    
class ClientScope(BaseModel):
    """
    Represents a scope for a client.
    
    A scope is a permission that the client can request to allow it to access certain attributes of the user's client specific profile.
    
    Args:
        name (str): The 'name' of the scope.
        description (str): A description of the scope and what it allows the client to do.
        shareable (bool): Whether other clients can request access to this scope.
        developer_only (bool): Whether the scope is only available to developers.
        is_personal_scope (bool): Whether the scope only allows the specific user to access the associated attributes or (if False) allow other linked users to access the associated attributes if they have the scope.
        associated_attributes (List[ScopeAttribute]): The attributes (profile metadata) that this scope controls.
    """
    name: str
    description: str
    shareable: bool
    developer_only: bool
    is_personal_scope: bool
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