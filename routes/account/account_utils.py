from main import db_manager

def check_user_exists(username: str) -> bool:
    """
    Check if a user exists in the database.

    Args:
        username (str): The username of the user.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    return bool(db_manager.accounts_interface.get_account(username=username))