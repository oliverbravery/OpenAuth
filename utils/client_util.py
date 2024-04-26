
from models.client_models import Client, ClientScope


def convert_names_to_scopes(scope_names: list[str], client: Client) -> list[ClientScope]:
    """
    Converts a list of scope names to a list of ClientScope objects. 
    
    NOTE: This method assumes that the scope names are valid for the client.

    Args:
        scope_names (list[str]): List of scope names.
        client (Client): The client object that the scopes belong to.

    Returns:
        list[ClientScope]: List of ClientScope objects. None if a scope name does not exist for the client.
    """
    client_scopes: list[ClientScope] = []
    located: bool
    for s_name in scope_names:
        located = False
        for c_scope in client.scopes:
            if s_name == c_scope.name:
                client_scopes.append(c_scope)
                located = True
        if not located: return None
    return client_scopes