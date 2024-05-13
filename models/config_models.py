from cryptography.fernet import Fernet
from pydantic import BaseModel, field_validator
from functools import partial
from pathlib import Path
from enum import Enum
import re


def must_be_a_valid_path(cls, v):
    if not Path(v).exists():
        raise ValueError(f'File path does not exist: "{v}"')
    return v

def hex_validator(v, num_bits: int):
    if not re.fullmatch(f"[0-9a-fA-F]{{{num_bits // 4}}}", v):
        raise ValueError(f"Value must be a {num_bits}-bit hex string. Got: {v}")
    return v

def fernet_key_validator(v):
    try:
        fernet: Fernet = Fernet(v)
        return v
    except Exception:
        raise ValueError(f"Value must be a valid Fernet key. Got: {v}")

class TokenAlgorithm(str, Enum):
    RS256 = "RS256"
    
class DevConfig(BaseModel):
    """
    Represents the configuration for the development environment.

    Args:
        reCAPTCHA_enabled (bool): Whether reCAPTCHA is enabled.
    """
    reCAPTCHA_enabled: bool
    
class ApiConfig(BaseModel):
    host: str
    port: int

class DatabaseConfig(BaseModel):
    host: str
    port: int
    name: str
    username: str
    password: str
    
class JWTConfig(BaseModel):
    private_key_path: str
    public_key_path: str
    token_algorithm: TokenAlgorithm
    access_token_expire: int
    refresh_token_expire: int

    _private_key_path_validator = field_validator('private_key_path')(must_be_a_valid_path)
    _public_key_path_validator = field_validator('public_key_path')(must_be_a_valid_path)
    
class GoogleRecaptchaConfig(BaseModel):
    secret_key: str
    site_key: str
    
class AuthConfig(BaseModel):
    authentication_code_secret: str
    
    _authentication_code_secret_validator = field_validator('authentication_code_secret')(fernet_key_validator)
    
class DefaultClientConfig(BaseModel):
    client_id: str
    client_secret: str
    client_model_path: str
    
    _client_id_validator = field_validator('client_id')(partial(hex_validator, num_bits=128))
    _client_secret_validator = field_validator('client_secret')(partial(hex_validator, num_bits=256))
    _client_model_path_validator = field_validator('client_model_path')(must_be_a_valid_path)
    