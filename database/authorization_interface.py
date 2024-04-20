from database.db_generic_interface import DBGenericInterface
from pymongo.database import Database
from database.models import DBCollection, Authorization

class AuthorizationInterface(DBGenericInterface):
    """
    Class for interacting with the authorization collection in the database.
    Derived from the DBGenericInterface class.
    """
    def __init__(self, database: Database) -> None:
        """
        Initializes the AuthorizationInterface object, creating the authorization collection if it does not already exist.
        """
        super().__init__(database=database, db_collection=DBCollection.AUTHORIZATION.value)
        
    def add_authorization(self, authorization: Authorization) -> int:
        """
        Adds an authorization to the database.

        Returns:
            int: 0 if the authorization was added successfully, -1 otherwise.
        """
        return self.add_generic(object=authorization)