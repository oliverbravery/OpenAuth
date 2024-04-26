from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AccountRole(str, Enum):
    """
    Enum class for representing the different roles an account can have
    """
    STANDARD = "standard"
    DEVELOPER = "developer"
    
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
    
class Profile(BaseModel):
    """
    Represents a profile for a client stored in the user's account.

    Args:
        client_id (str): The client_id of the application associated with the profile.
        scopes (List[ProfileScope]): The scopes that the application is allowed to access.
        metadata (Dict[str, any]): Additional attributes that the application has stored in the user's profile. Attributes are defined by the client. (Attribute name: Attribute value)
    """
    client_id: str
    scopes: List[ProfileScope] = []
    metadata: Dict[str, Any] = {}
    
class Account(BaseModel):
    """
    Represents a user account in the auth service.

    Args:
        username (str): The unique username of the user.
        display_name (str): The display name of the user.
        email (str): The email of the user.
        hashed_password (str): The hashed password of the user.
        hashed_totp_pin (Optional[str]): The hashed TOTP pin of the user.
        profiles (List[Profile]): The profiles associated with the user.
        account_role (AccountRole): The role of the user in the auth service. Defaults to 'standard'.
    """
    username: str
    display_name: str
    email: str
    hashed_password: str
    hashed_totp_pin: Optional[str] = None
    profiles: List[Profile] = []
    account_role: AccountRole = AccountRole.STANDARD
    
    def get_profile(self, client_id: str) -> Optional[Profile]:
        """
        Get the profile of the user for the given application.

        Args:
            client_id (str): The client_id of the application.

        Returns:
            Optional[Profile]: The profile of the user for the given application. None if the profile does not exist.
        """
        for profile in self.profiles:
            if profile.client_id == client_id:
                return profile
        return None