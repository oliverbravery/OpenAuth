from models.client_models import Client
from models.scope_models import AccountAttribute
from models.util_models import ClientCredentialType
from utils.client_utils import generate_client_credential
from common import db_manager
from utils.hash_utils import hash_string
from validators.client_validators import validate_client_developers, validate_metadata_attributes, validate_profile_defaults
from validators.scope_validators import validate_client_scopes


def generate_unique_client_id() -> str:
    """
    Generate a unique client id for a client.

    Returns:
        str: The generated unique client id.
    """
    generated_client_id: str = generate_client_credential(credential_type=ClientCredentialType.ID)
    if db_manager.clients_interface.get_client(client_id=generated_client_id):
        return generate_unique_client_id()
    return generated_client_id

def get_shared_read_attributes(client_id: str) -> list[AccountAttribute]:
    """
    Get the shared read attributes for a client.

    Args:
        client_id (str): The client id of the client.

    Returns:
        list[str]: The shared read attributes.
    """
    client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return None
    return client.shared_read_attributes

def load_client_model(client_id: str, client_secret: str, redirect_port: int, 
                      redirect_host: str, client_model_path: str) -> Client:
    """
    Loads the client model from the file path provided in the environment variables.
    
    Validates the client model to ensure it is in the correct format and adds the client_id and client_secret from the environment variables.
    
    NOTE: Assumes the parameters are valid.
    
    Args:
        client_id (str): The client id of the client.
        client_secret (str): The client secret of the client.
        redirect_port (int): The port to redirect to after login.
        redirect_host (str): The host to redirect to after login.
        client_model_path (str): The path to the client model file.
    
    Raises:
        ValueError: If the client model is not in the valid Client format.

    Returns:
        Client: The client model object.
    """
    with open(client_model_path, "r") as client_model_file:
        try:
            default_client: Client = Client.model_validate_json(client_model_file.read())
            default_client.client_id = client_id
            default_client.client_secret_hash = hash_string(plaintext=client_secret)
            default_client.redirect_uri = f"http://{redirect_host}:{redirect_port}/account/login/callback"
            if not validate_client_developers(client=default_client): raise ValueError("Client model does not have valid developers.")
            if not validate_metadata_attributes(client=default_client): raise ValueError("Metadata attributes are not unique.")
            if not validate_profile_defaults(client=default_client): raise ValueError("Profile defaults are not valid.")
            if not validate_client_scopes(client=default_client): raise ValueError("Client model does not have valid scopes.")
            return default_client
        except ValueError as e:
            raise ValueError(f"Client model in file {client_model_path} is not in the valid Client format. {e}")