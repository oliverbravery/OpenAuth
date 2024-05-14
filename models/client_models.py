from enum import Enum
from typing import List, Dict, Any
import datetime
from pydantic import BaseModel
from models.scope_models import AccountAttribute, ClientScope

class ClientDeveloper(BaseModel):
    """
    Represents what scopes a developer has access to for a client.
    
    Args:
        username (str): The unique username of the developer.
        scopes (List[str]): The scopes that the developer has access to for the client. Must be a developer only scope.
    """
    username: str
    scopes: List[str]
    
class MetadataType(str, Enum):
    """
    Represents the possible types for a metadata attribute.
    """
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    UNSTRUCTURED = "unstructured"
    
    def get_pythonic_type(self) -> type:
        """
        Get the Pythonic type for the metadata attribute.
        
        Returns:
            type: The Pythonic type for the metadata attribute.
        """
        if self == MetadataType.STRING: return str
        if self == MetadataType.INTEGER: return int
        if self == MetadataType.FLOAT: return float
        if self == MetadataType.BOOLEAN: return bool
        if self == MetadataType.DATETIME: return datetime.datetime
        if self == MetadataType.UNSTRUCTURED: return dict
    
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
        client_secret_hash (str): A long random string that is used to authenticate the application. Stored as a hash.
        name (str): The name of the application.
        description (str): A description of the application and why it needs access to certain scopes.
        redirect_uri (str): The URI to which the user is redirected after granting or denying access to the application.
        developers (List[ClientAdmin]): The list of developers that have access to the client.
        profile_metadata_attributes (List[MetadataAttribute]): The metadata attributes that the client can store in the user's profile.
        profile_defaults (dict[str, any]): Any default values that the client wants to store in the user's profile.
        scopes (list[ClientScope]): List of all custom scopes created by the client to control access to ONLY client profile specific metadata attributes.
        shared_read_attributes (list[AccountAttribute]): List of all shared attributes that the client and other linked accounts can read from the user's account.
    """
    client_id: str
    client_secret_hash: str
    name: str
    description: str
    redirect_uri: str
    developers: List[ClientDeveloper] = []
    profile_metadata_attributes: list[MetadataAttribute] = []
    profile_defaults: Dict[str, Any] = {}
    scopes: list[ClientScope]
    shared_read_attributes: list[AccountAttribute]
    