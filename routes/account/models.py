from fastapi.param_functions import Form

class UserRegistrationForm:
    """
    A class used to represent a new account form. 
    It is used to parse the data from the request body when registering a new account.
    """
    def __init__(
        self,
        username: str = Form(),
        password: str = Form(),
        email: str = Form(),
        display_name: str = Form(),
    ):
        self.username: str = username
        self.password: str = password
        self.email: str = email
        self.display_name: str = display_name