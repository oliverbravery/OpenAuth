from enum import Enum

class DBCollection(Enum):
    """
    Enum class for the database collections
    """
    AUTHORIZATION = "authorization"
    ACCOUNTS = "accounts"
    APPLICATIONS = "applications"