import pymongo
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, DeleteResult, UpdateResult

class DBGenericInterface:
    """
    Base class for database interactions. It provides the basic functionalities for interacting with the database.
    """
    db: Database
    db_collection: str
    
    def __init__(self, database: Database, db_collection: str) -> None:
        """
        Initializes the BaseDatabase object, creating the specified database collection if it does not already exist.

        Args:
            database (Database): Mongo Database object. Used for interacting with the database.
            db_collection (str): Collection to be used for the database interactions. 
        """
        self.db = database
        self.db_collection = db_collection
        try:
            self.db.validate_collection(self.db_collection)
        except pymongo.errors.OperationFailure:
            self.create_collection()
                
    def create_collection(self) -> int:
        """
        Creates a collection in the database. 

        Returns:
            int: 0 if the collection was created successfully, -1 otherwise (e.g. collection already exists).
        """
        try:
            response: Collection = self.db.create_collection(self.db_collection)
            return 0 if response is not None else -1
        except pymongo.errors.CollectionInvalid:
            return -1
        
    def get_generic(self, search_params: dict[str,any], 
                    object_class: object, filter_array: dict[str, any] = {}) -> object | None:
        """
        Generic function for getting an object from the database.

        Args:
            search_params (dict[str,any]): The search parameters of the object to get. For example, {"username": "test"} will return the object with the username "test".
            object_class (object): The class of the object to return.
            filter_array (dict[str, any], optional): Any NOSQL MongoDB complient filters to add to the query. Defaults to {}.

        Returns:
            object | None: The object if it exists, None otherwise.
        """
        result: any | None = self.db[self.db_collection].find_one(search_params, filter_array)
        if result is None:
            return None
        else:
            return object_class(**result)
        
    def get_generics(self, search_params: dict[str,any],
                     object_class: object, filter_array: dict[str, any] = {}) -> list[object] | None:
        """
        Generic function for getting multiple objects from the database.

        Args:
            search_params (dict[str,any]): The search parameters of the objects to get. For example, {"username": "test"} will return a list of objects with the username "test".
            object_class (object): The class of the object to return.
            filter_array (dict[str, any], optional): Any NOSQL MongoDB complient filters to add to the query. Defaults to {}.

        Returns:
            list[object] | None: The list of objects if they exist, None otherwise.
        """
        result: any | None = self.db[self.db_collection].find(search_params, filter_array)
        if result is None:
            return None
        else:
            return [object_class(**item) for item in result]
        
    def add_generic(self, object: object) -> int:
        """
        Generic function for adding an object to the database.

        Args:
            object (object): The data to add to the collection in it's object form.

        Returns:
            int: 0 if the object was added successfully, -1 otherwise.
        """
        inserted_value: InsertOneResult = self.db[self.db_collection].insert_one(object.dict())
        if inserted_value.inserted_id:
            return 0
        else:
            return -1
        
    def remove_generic(self, search_params: dict[str,any]) -> int:
        """
        Generic function for removing an object from the database.

        Args:
            search_params (dict[str,any]): The search parameters of the object to remove. For example, {"username": "test"} will remove the object with the username "test".

        Returns:
            int: 0 if the object was removed successfully, -1 otherwise.
        """
        deleted_value: DeleteResult = self.db[self.db_collection].delete_one(search_params)
        if deleted_value.deleted_count > 0:
            return 0
        else:
            return -1
        
    def update_generic(self, search_params: dict[str,any], update_params: dict[str,any], array_filters: dict[str, any] = []) -> int:
        """
        Generic function for updating an object in the database.

        Args:
            search_params (dict[str,any]): The search parameters of the object to update. For example, {"username": "test"} will update the object with the username "test".
            update_params (dict[str,any]): The parameters to update the object with. For example, {"password": "new_password"} will update the objects found with the search_params.
            array_filters (dict[str, any], optional): Any NOSQL MongoDB complient filters to add to the query. Defaults to [].

        Returns:
            int: 0 if the object was updated successfully, -1 otherwise.
        """
        update_value: UpdateResult = self.db[self.db_collection].update_one(search_params, update_params, array_filters=array_filters)
        if update_value.matched_count > 0:
            return 0
        else: 
            return -1