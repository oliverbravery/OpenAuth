from pydantic import BaseModel
from typing import List, Optional

class RegisteredApplication(BaseModel):
    """
    Represents a registered application in the auth service. 
    An application is a client (app) that can request access to a user's account and store application-specific data in the user's profile.
    
    Args:
        client_id (str): The unique attribute used to identify and differentiate applications.
        client_secret (str): A long random string that is used to authenticate the application.
        name (str): The name of the application.
    """
    client_id: str
    client_secret: str
    name: str
    
class Profile(BaseModel):
    """
    Represents a profile for an app stored in the user's account.

    Args:
        client_id (str): The client_id of the application associated with the profile.
        role (str): The role of the user according to the application.
        scopes (List[str]): The scopes that the application is allowed to access.
    """
    client_id: str
    role: str
    scopes: List[str] = []
    
class Account(BaseModel):
    """
    Represents a user account in the auth service.

    Args:
        user_id (str): The unique attribute used to identify and differentiate users.
        username (str): The username of the user.
        display_name (str): The display name of the user.
        email (str): The email of the user.
        hashed_password (str): The hashed password of the user.
        hashed_totp_pin (Optional[str]): The hashed TOTP pin of the user.
        profiles (List[Profile]): The profiles associated with the user.
    """
    user_id: str
    username: str
    display_name: str
    email: str
    hashed_password: str
    hashed_totp_pin: Optional[str] = None
    profiles: List[Profile] = []
    
class Authorization(BaseModel):
    """
    Represents temporary authorization data for users.

    Args:
        user_id (str): The user_id of the user.
        code_challenge (Optional[str]): A challenge generated by the user for PKCE.
        auth_code (Optional[str]): The temporary code challenge generated by the auth service for PKCE.
        hashed_refresh_token (Optional[str]): The hashed refresh token generated by the auth service.
    """
    user_id: str
    code_challenge: Optional[str] = None
    auth_code: Optional[str] = None
    hashed_refresh_token: Optional[str] = None