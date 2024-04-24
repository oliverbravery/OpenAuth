from database.db_manager import DBManager
from dotenv import load_dotenv
import os

load_dotenv(override=True)

MONGO_PORT: int = os.getenv("MONGO_PORT")
MONGO_HOST: str = os.getenv("MONGO_HOST")
MONGO_ROOT_USERNAME: str = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_ROOT_PASSWORD: str = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_DATABASE_NAME: str = os.getenv("DMONGO_DATABASE_NAME")

fernet: Fernet = Fernet(os.getenv("AUTH_CODE_SECRET"))

recaptcha_secret_key: str = os.getenv("RECAPTCHA_SECRET_KEY")
if not recaptcha_secret_key: raise ValueError("RECAPTCHA_SECRET_KEY not set in environment variables.")
google_verify_url: str = f"https://www.google.com/recaptcha/api/siteverify?secret={recaptcha_secret_key}&response="

token_manager: TokenManager = TokenManager(
    access_token_expire_time=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")),
    refresh_token_expire_time=int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")),
    private_key_path=str(os.getenv("JWT_PRIVATE_PEM_PATH")),
    public_key_path=str(os.getenv("JWT_PUBLIC_PEM_PATH")),
    token_algorithm=str(os.getenv("TOKEN_ALGORITHM"))
)

db_manager: DBManager = DBManager(
    connection_string=get_connection_string(
        port=MONGO_PORT, 
        host=MONGO_HOST, 
        username=MONGO_ROOT_USERNAME, 
        password=MONGO_ROOT_PASSWORD), 
    db_name=MONGO_DATABASE_NAME)
