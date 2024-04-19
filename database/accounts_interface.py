from database.db_generic_interface import DBGenericInterface
from pymongo.database import Database
from database.models import DBCollection
from models import Account

class AccountsInterface(DBGenericInterface):
    """
    Class for interacting with the accounts collection in the database.
    Derived from the DBGenericInterface class.
    """
    def __init__(self, database: Database) -> None:
        """
        Initializes the AccountsInterface object, creating the accounts collection if it does not already exist.
        """
        super().__init__(database=database, db_collection=DBCollection.ACCOUNTS.value)
        
    def get_account(self, username: str) -> Account | None:
        """
        Gets an account from the database based on the username.

        Args:
            username (str): The username of the account to get.

        Returns:
            Account | None: The account if it exists, None otherwise.
        """
        return self.get_generic(search_params={"username": username}, object_class=Account)
    
    def add_account(self, account: Account) -> int:
        """
        Adds an account to the database.

        Args:
            account (Account): The account object to add.

        Returns:
            int: 0 if the account was added successfully, -1 otherwise.
        """
        return self.add_generic(object=account)
    
    def update_account(self, account: Account) -> int:
        """
        Updates an account in the database.

        Args:
            account (Account): The account object to update.

        Returns:
            int: 0 if the account was updated successfully, -1 otherwise.
        """
        return self.update_generic(search_params={"username": account.username}, update_params={"$set": account.model_dump()})