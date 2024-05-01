import bcrypt


def verify_hash(plaintext: str, urlsafe_hash: str) -> bool:
    """
    Verifies a plaintext string against a URL safe hash.

    Args:
        plaintext (str): Plaintext string to be verified.
        urlsafe_hash (str): URL safe hash to be verified against.

    Returns:
        bool: True if the plaintext string matches the URL safe hash, False otherwise.
    """
    return bcrypt.checkpw(plaintext.encode('utf-8'), urlsafe_hash.encode('utf-8'))

def hash_string(plaintext: str) -> str:
    """
    Hash a plaintext string using bcrypt and return the URL safe hash.

    Args:
        plaintext (str): Plaintext string to be hashed.

    Returns:
        str: URL safe hash of the plaintext string.
    """
    salt = bcrypt.gensalt()
    hashed_token = bcrypt.hashpw(plaintext.encode('utf-8'), salt)
    return hashed_token.decode('utf-8')