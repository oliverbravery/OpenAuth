def get_connection_string(port: int, host: str, username: str, password: str) -> str:
    """
    Composes a connection string for a MongoDB database.

    Args:
        port (int): Port number for the MongoDB database.
        host (str): Hostname for the MongoDB database.
        username (str): Username for the MongoDB database.
        password (str): Password for the MongoDB database.

    Returns:
        str: Composed connection string for the MongoDB database.
    """
    return f"mongodb://{username}:{password}@{host}:{port}"