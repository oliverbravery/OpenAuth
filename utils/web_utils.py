from fastapi.datastructures import FormData
from pydantic import BaseModel


def configure_redirect_uri(base_uri: str, query_parameters: dict[str, str]) -> str:
    """
    Configure the redirect uri with the query parameters.

    Args:
        base_uri (str): The base uri of the redirect.
        query_parameters (dict[str, str]): The query parameters to be added to the redirect uri.

    Returns:
        str: The complete redirect uri with the query parameters.
    """
    complete_uri: str = base_uri + "?"
    for key, value in query_parameters.items():
        complete_uri += f"{key}={value}&"
    return complete_uri

def form_to_object(form_data: FormData, object_class: BaseModel) -> object:
    """
    Convert form data to a Pydantic object.

    Args:
        form_data (FormData): The form data to be converted.
        object_class (BaseModel): The Pydantic object class to convert the form data to.

    Returns:
        object: The Pydantic object with the form data.
    """
    form_data_dict: dict = {}
    for key, value in form_data.items():
        form_data_dict[key] = value
    return object_class.model_construct(**form_data_dict)