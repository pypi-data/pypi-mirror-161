from authena_python_sdk.client import Client
from authena_python_sdk.models.group import Group


def test_FUNC_client_group_get_WITH_valid_configuration_EXPECT_group_retrieved(sdk_client: Client, group: Group) -> None:
    """
    Check whether with good configuration a group can be retrieved.

    :param sdk_client: Authena SDK client.
    :param group: Group fixture.

    :return: No return.
    """
    # Ensure group exists.
    retrieved_group = sdk_client.group.get(group.group_id)

    assert retrieved_group.group_id == group.group_id
