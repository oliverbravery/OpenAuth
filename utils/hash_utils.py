def verify_hash(plaintext: str, urlsafe_hash: str) -> bool:
    """
    Verifies a plaintext string against a URL safe hash.

    Args:
        plaintext (str): Plaintext string to be verified.
        urlsafe_hash (str): URL safe hash to be verified against.

    Returns:
        bool: True if the plaintext string matches the URL safe hash, False otherwise.
    """
    hashed_bytes: bytes = urlsafe_b64decode(urlsafe_hash.encode('utf-8'))
    return bcrypt.checkpw(plaintext.encode('utf-8'), hashed_bytes)

def hash_string(plaintext: str) -> str:
    """
    Hash a plaintext string using bcrypt and return the URL safe hash.

    Args:
        plaintext (str): Plaintext string to be hashed.

    Returns:
        str: URL safe hash of the plaintext string.
    """
    hashed_bytes: bytes = bcrypt.hashpw(plaintext.encode('utf-8'), bcrypt.gensalt())
    urlsafe_hash: str = urlsafe_b64encode(hashed_bytes).decode('utf-8')
    return urlsafe_hash