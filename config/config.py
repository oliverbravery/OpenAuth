from models.config_models import AuthConfig, DatabaseConfig, DefaultClientConfig, GoogleRecaptchaConfig, JWTConfig
from dotenv import load_dotenv
from os import getenv

load_dotenv(override=True)

class Config:
    """
    Used to load and store the environment variables.
    """
    database_config: DatabaseConfig
    jwt_config: JWTConfig
    google_recaptcha_config: GoogleRecaptchaConfig
    auth_config: AuthConfig
    default_client_config: DefaultClientConfig
    
    def __init__(self):
        self.__load_environment_variables()
    
    def __load_environment_variables(self):
        """
        Loads the environment variables.
        """
        self.database_config = DatabaseConfig(
            host=getenv("AUTH_MONGO_HOST"),
            port=int(getenv("AUTH_MONGO_PORT")),
            name=getenv("AUTH_MONGO_DATABASE_NAME"),
            username=getenv("AUTH_MONGO_USERNAME"),
            password=getenv("AUTH_MONGO_PASSWORD")
        )
        self.jwt_config = JWTConfig(
            private_key_path=getenv("AUTH_JWT_PRIVATE_PEM_PATH"),
            public_key_path=getenv("AUTH_JWT_PUBLIC_PEM_PATH"),
            token_algorithm=getenv("AUTH_TOKEN_ALGORITHM"),
            access_token_expire=int(getenv("AUTH_ACCESS_TOKEN_EXPIRE")),
            refresh_token_expire=int(getenv("AUTH_REFRESH_TOKEN_EXPIRE"))
        )
        self.google_recaptcha_config = GoogleRecaptchaConfig(
            secret_key=getenv("AUTH_RECAPTCHA_SECRET_KEY"),
            site_key=getenv("AUTH_RECAPTCHA_SITE_KEY")
        )
        self.auth_config = AuthConfig(
            authentication_code_secret=getenv("AUTH_CODE_SECRET")
        )
        self.default_client_config = DefaultClientConfig(
            client_id=getenv("AUTH_DEFAULT_CLIENT_ID"),
            client_secret=getenv("AUTH_DEFAULT_CLIENT_SECRET"),
            client_model_path=getenv("AUTH_DEFAULT_CLIENT_MODEL_PATH")
        )