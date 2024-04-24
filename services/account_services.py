def register_account_in_db_collections(new_account: Account) -> int:
    """
    Register a new account in the database collections.
    Adds the new account to the accounts collection and the authorization collection.

    Args:
        new_account (Account): The account to be registered.

    Returns:
        int: 0 if the account was successfully registered, -1 otherwise.
    """
    response: int = db_manager.accounts_interface.add_account(account=new_account)
    if response == -1: return -1
    authorization_object: Authorization = Authorization(username=new_account.username)
    response: int = db_manager.authorization_interface.add_authorization(authorization=authorization_object)
    if response == -1: 
        response: int = db_manager.accounts_interface.delete_account(username=new_account.username)
        return -1
    return 0

def create_profile_if_not_exists(client_id: str, username: str) -> int:
    client: Client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return -1
    # go through the client defaults and construct the client's profile based on them
    new_profile: Profile = Profile(
        client_id=client_id,
        role=client.get_profile_default(key="role"),
        scopes=[],
        metadata=
        )
    
def get_client_concent_details(client_id: str, scopes: list[str]) -> ConcentDetails:
    """
    Fetches the details from the client required for the consent form.

    Args:
        client_id (str): The client id of the application.
        scopes (list[str]): The scopes requested by the client.

    Returns:
        ConcentDetails: A model containing the details required for the consent form.
    """
    client: Client = db_manager.clients_interface.get_client(client_id=client_id)
    if not client: return None
    return ConcentDetails(name=client.name, 
                          description=client.description, 
                          scopes_description=client.scopes,
                          client_redirect_uri=client.redirect_uri)
    
def enroll_account_as_developer(account: Account) -> int:
    """
    Enrolls a user as a developer.

    Args:
        account (Account): The account to enroll as a developer.

    Returns:
        int: 0 if the account was successfully enrolled as a developer, -1 otherwise.
    """
    account.account_role = AccountRole.DEVELOPER
    return db_manager.accounts_interface.update_generic(account)