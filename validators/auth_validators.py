def verify_authorization_code(auth_code: str, username: str) -> bool:
    """
    Verify an authorization code.

    Args:
        auth_code (str): The authorization code.
        username: (str): The username of the user to be authorized.
        
    Returns:
        bool: True if the authorization code is valid, False otherwise.
    """
    authorization: Authorization = db_manager.authorization_interface.get_authorization(username=username)
    if not authorization: return False
    return authorization.auth_code == auth_code

def verify_code_challenge(code_challenge: str, code_verifier: str) -> bool:
    """
    Verify a code challenge using SHA-256.

    Args:
        code_challenge (str): The code challenge.
        code_verifier (str): The code verifier.
        
    Returns:
        bool: True if the code challenge is valid, False otherwise.
    """
    generated_code_challenge: str = urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode()
    return code_challenge == generated_code_challenge