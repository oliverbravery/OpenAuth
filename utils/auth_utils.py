def generate_code_challenge_and_verifier() -> tuple[str, str]:
    """
    Generate a code challenge and code verifier for PKCE.

    Returns:
        tuple[str, str]: The code challenge and code verifier as a tuple (code_challenge, code_verifier).
    """
    code_verifier: str = token_urlsafe(256)
    code_challenge: str = urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode()
    return code_challenge, code_verifier

def generate_authorization_code(username: str) -> tuple[str, str]:
    """
    Generate an encrypted authorization code with a username.
        
    Args:
        username (str): The username of the user to be authorized.

    Returns:
        tuple[str, str]: The generated URL safe encrypted authorization code and the plaintext authorization code (encrypted auth code, auth_code).
    """
    auth_code: str = token_urlsafe(32)
    combined_code: str = f"{username}:{auth_code}"
    encrypted_code: bytes = fernet.encrypt(combined_code.encode())
    url_safe: str = urlsafe_b64encode(encrypted_code).decode()
    return url_safe, auth_code

def decrypt_authorization_code(auth_code: str) -> tuple[str, str]:
    """
    Decrypt an encrypted authorization code.

    Args:
        auth_code (str): The encrypted authorization code.
        
    Returns:
        tuple[str, str]: The username and the authorization code as a tuple (username, auth_code).
    """
    decrypted_combined_code: str = fernet.decrypt(urlsafe_b64decode(auth_code.encode())).decode()
    return decrypted_combined_code.split(":")[0], decrypted_combined_code[len(decrypted_combined_code.split(":")[0])+1:]