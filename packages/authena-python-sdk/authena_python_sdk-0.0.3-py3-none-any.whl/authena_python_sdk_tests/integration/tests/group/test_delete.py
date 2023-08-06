from time import sleep

import pytest
from b_lambda_layer_common.exceptions.container.not_found_error import NotFoundError

from authena_python_sdk.client import Client
from authena_python_sdk.models.group import Group


def test_FUNC_client_group_delete_WITH_valid_configuration_EXPECT_group_deleted(sdk_client: Client, group: Group) -> None:
    """
    Check whether with good configuration a group can be deleted.

    :param sdk_client: Authena SDK client.
    :param group: Group fixture.

    :return: No return.
    """
    # Ensure group exists.
    retrieved_group = sdk_client.group.get(group.group_id)
    assert retrieved_group.group_id == group.group_id

    # Delete the group.
    sdk_client.group.delete(group_id=retrieved_group.group_id)

    # Sleep for the cache to be cleared.
    sleep(11)

    # Try to get deleted group. Should fail.
    with pytest.raises(NotFoundError):
        sdk_client.group.get(group_id=retrieved_group.group_id)
