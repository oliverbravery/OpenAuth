from fastapi.param_functions import Form

class LoginCredentialsForm:
    """
    A class used to represent the data required to authenticate a user. 
    It is used to parse the data from the request body when validating a user.
    """
    def __init__(
        self,
        username: str = Form(),
        password: str = Form(),
    ):
        self.username: str = username
        self.password: str = password