from fastapi import FastAPI
from database.db_manager import DBManager
from dotenv import load_dotenv
import os

load_dotenv(override=True)
MONGO_PORT: int = os.getenv("MONGO_PORT")
MONGO_HOST: str = os.getenv("MONGO_HOST")
MONGO_ROOT_USERNAME: str = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_ROOT_PASSWORD: str = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_DATABASE_NAME: str = os.getenv("DMONGO_DATABASE_NAME")

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

mongo_connection_string: str = get_connection_string(port=MONGO_PORT, 
                                                     host=MONGO_HOST, 
                                                     username=MONGO_ROOT_USERNAME, 
                                                     password=MONGO_ROOT_PASSWORD)

db_manager: DBManager = DBManager(connection_string=mongo_connection_string, db_name=MONGO_DATABASE_NAME)

app: FastAPI = FastAPI()

from routes.account import account_router
app.include_router(account_router.router)

from routes.authentication import authentication_router
app.include_router(authentication_router.router)

@app.get("/")
async def root():
    return {"status": "Success", "message": "Welcome to the API!"}