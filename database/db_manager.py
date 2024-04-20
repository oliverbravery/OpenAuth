import pymongo
from pymongo import MongoClient
from pymongo.database import Database
from database.accounts_interface import AccountsInterface
from database.authorization_interface import AuthorizationInterface

class DBManager:
    """
    Class for managing the connection to the database and providing access to the different collection specific interfaces.
    This class should only be instantiated once and used throughout the project for all Database interactions.
    """
    __db_client: MongoClient
    __db: Database
    
    def __init__(self, connection_string: str, db_name: str) -> None:
        """
        Initializes the DBManager object. 
        It creates a connection to the database and initializes the different collection specific interface objects.

        Args:
            connection_string (str): String containing the connection information for the database.
            db_name (str): Name of the database to connect to.
        """
        self.__db_client: MongoClient = pymongo.MongoClient(connection_string)
        self.__db: Database = self.__db_client[db_name]
        # Other collection specific interfaces can be added here for a more modular approach.
        # For example, if the project has a users collection, the UsersDBInterface can be added here: 
        # self.users_interface: UsersDBInterface = UsersDBInterface(database=self.__db)
        self.accounts_interface: AccountsInterface = AccountsInterface(database=self.__db) 
        self.authorization_interface: AuthorizationInterface = AuthorizationInterface(database=self.__db)