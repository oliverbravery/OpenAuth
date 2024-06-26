from database.db_generic_interface import DBGenericInterface
from pymongo.database import Database
from models.util_models import DBCollection
from models.client_models import Client

class ClientsInterface(DBGenericInterface):
    """
    Class for interacting with the clients collection in the database.
    Derived from the DBGenericInterface class.
    """
    def __init__(self, database: Database) -> None:
        """
        Initializes the ClientsInterface object, creating the clients collection if it does not already exist.
        """
        super().__init__(database=database, db_collection=DBCollection.CLIENTS.value)
        
    def get_client(self, client_id: str) -> Client:
        """
        Gets the client with the specified client_id from the clients collection.
        """
        return self.get_generic(search_params={"client_id": client_id}, object_class=Client)
    
    def add_client(self, client: Client) -> int:
        """
        Adds a client to the database.

        Args:
            client (Client): The Client object to add to the database.

        Returns:
            int: 0 if the client was added successfully, -1 otherwise.
        """
        return self.add_generic(object=client)