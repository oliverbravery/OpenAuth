from models.scope_models import AccountAttribute
from models.util_models import ClientCredentialType
from utils.client_utils import generate_client_credential
from common import db_manager


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