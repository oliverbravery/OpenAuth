from database.db_generic_interface import DBGenericInterface
from pymongo.database import Database
from database.models import DBCollection
from models import Account

class db_accounts_interface(DBGenericInterface):
    """
    Class for interacting with the accounts collection in the database.
    Derived from the DBGenericInterface class.
    """
    def __init__(self, database: Database) -> None:
        """
        Initializes the db_accounts_interface object, creating the accounts collection if it does not already exist.
        """
        super().__init__(database=database, db_collection=DBCollection.ACCOUNTS.value)
        
    def get_account(self, user_id: str) -> Account | None:
        """
        Gets an account from the database based on the user_id.

        Args:
            user_id (str): The user_id of the account to get.

        Returns:
            Account | None: The account if it exists, None otherwise.
        """
        return self.get_generic(search_params={"user_id": user_id}, object_class=Account)