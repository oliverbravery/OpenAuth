from authentication_utils import hash_string, verify_hash

class PasswordManager:
    """
    Stateless utility class for managing passwords. 
    It provides methods for hashing and verifying passwords.
    """
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifies if the plaintext password matches the hashed password.

        Args:
            plain_password (str): Non-hashed password.
            hashed_password (str): Hashed password.

        Returns:
            bool: True if the plaintext password matches the hashed password, False otherwise.
        """
        return verify_hash(plaintext=plain_password, urlsafe_hash=hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Returns a salted and hashed password.

        Args:
            password (str): Non-hashed password.

        Returns:
            str: Salted and hashed password.
        """
        return hash_string(plaintext=password)