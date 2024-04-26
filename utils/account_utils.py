from models.client_models import MetadataAttribute


def generate_default_metadata(profile_metadata_attributes: list[MetadataAttribute], 
                              profile_defaults: dict[str, any]) -> dict[str, any]:
    """
    Generate the default metadata for a profile.

    Args:
        profile_metadata_attributes (list[MetadataAttribute]): The metadata attributes that the client can store in the user's profile.
        profile_defaults (dict[str, any]): Any default values that the client wants to store in the user's profile.

    Returns:
        dict[str, any]: The default metadata for the profile.
    """
    new_metadata: dict[str, any] = {metadata.name:None for metadata in profile_metadata_attributes}
    for key, value in profile_defaults.items():
        if key in new_metadata:
            new_metadata[key] = value
    return new_metadata