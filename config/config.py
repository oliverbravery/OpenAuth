from models.client_models import Client
from models.config_models import ApiConfig, AuthConfig, DatabaseConfig, DefaultClientConfig, GoogleRecaptchaConfig, JWTConfig
from dotenv import load_dotenv
from os import getenv
from utils.hash_utils import hash_string
from validators.client_validators import validate_client_developers, validate_metadata_attributes, validate_profile_defaults
from validators.scope_validators import validate_client_scopes

class Config:
    """
    Used to load and store the environment variables.
    """
    api_config: ApiConfig
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
        load_dotenv(override=True)
        self.api_config = ApiConfig(
            host=getenv("AUTH_HOST"),
            port=int(getenv("AUTH_PORT"))
        )
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
        
    def load_client_model(self) -> Client:
        """
        Loads the client model from the file path provided in the environment variables.
        
        Validates the client model to ensure it is in the correct format and adds the client_id and client_secret from the environment variables.
        
        Raises:
            ValueError: If the client model is not in the valid Client format.

        Returns:
            Client: The client model object.
        """
        with open(self.default_client_config.client_model_path, "r") as client_model_file:
            try:
                default_client: Client = Client.model_validate_json(client_model_file.read())
                default_client.client_id = self.default_client_config.client_id
                default_client.client_secret = hash_string(plaintext=self.default_client_config.client_secret)
                default_client.redirect_uri = f"http://{self.api_config.host}:{self.api_config.port}/account/login/callback"
                if not validate_client_developers(client=default_client): raise ValueError("Client model does not have valid developers.")
                if not validate_metadata_attributes(client=default_client): raise ValueError("Metadata attributes are not unique.")
                if not validate_profile_defaults(client=default_client): raise ValueError("Profile defaults are not valid.")
                if not validate_client_scopes(client=default_client): raise ValueError("Client model does not have valid scopes.")
                return default_client
            except ValueError as e:
                raise ValueError(f"Client model in file {self.default_client_config.client_model_path} is not in the valid Client format. {e}")
            
            