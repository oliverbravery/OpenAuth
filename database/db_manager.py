import pymongo
from pymongo import MongoClient
from pymongo.database import Database
from database.accounts_interface import AccountsInterface
from database.authorization_interface import AuthorizationInterface
from database.clients_interface import ClientsInterface
from models.client_models import Client
import re

from models.scope_models import ClientScope, ScopeAccessType, ScopeAttribute, Scopes
from utils.hash_utils import hash_string

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
        self.clients_interface: ClientsInterface = ClientsInterface(database=self.__db)
        
    def create_auth_service_client(self, AUTH_CLIENT_ID: str, AUTH_CLIENT_SECRET: str, 
                                     AUTH_SERVICE_HOST: str, AUTH_SERVICE_PORT: str):
        """
        Creates an authentication client for the application.
        
        Args: 
            AUTH_CLIENT_ID (str): The client id of the application.
            AUTH_CLIENT_SECRET (str): The client secret of the application.
            AUTH_SERVICE_HOST (str): The host of the authentication service.
            AUTH_SERVICE_PORT (str): The port of the authentication service.
        """
        if not AUTH_CLIENT_ID or not AUTH_CLIENT_SECRET:
            raise ValueError("AUTH_CLIENT_ID and AUTH_CLIENT_SECRET must be set in the environment.")
        if re.fullmatch(f"[0-9a-fA-F]{{{256 // 4}}}", AUTH_CLIENT_SECRET) is None or re.fullmatch(f"[0-9a-fA-F]{{{128 // 4}}}", AUTH_CLIENT_ID) is None:
            raise ValueError("AUTH_CLIENT_ID and AUTH_CLIENT_SECRET must be hexadecimal strings of the correct length.")
        if AUTH_SERVICE_HOST is None or AUTH_SERVICE_PORT is None:
            raise ValueError("AUTH_SERVICE_HOST and AUTH_SERVICE_PORT must be set to create authentication client.")
        auth_client_redirect_uri: str = f"http://{AUTH_SERVICE_HOST}:{AUTH_SERVICE_PORT}/account/login/callback"
        hashed_secret: str = hash_string(AUTH_CLIENT_SECRET)
        auth_client: Client = Client(client_id=AUTH_CLIENT_ID, client_secret_hash=hashed_secret, 
                                    name="Authentication Service", 
                                    description="Client for the authentication service", 
                                    redirect_uri=auth_client_redirect_uri,
                                    scopes=Scopes(
                                        client_scopes=[],
                                        external_scopes=[],
                                        account_scopes=[]
                                    ))
        self.clients_interface.add_client(client=auth_client)