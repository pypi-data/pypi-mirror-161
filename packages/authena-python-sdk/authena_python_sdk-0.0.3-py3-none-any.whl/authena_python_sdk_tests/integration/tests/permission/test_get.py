from typing import Callable

from authena_python_sdk.client import Client
from authena_python_sdk.models.group import Group
from authena_python_sdk.models.user import User


def test_FUNC_client_user_permissions_WITH_user_and_group_permissions_EXPECT_combined_permissions_returned(
        sdk_client: Client,
        group_function: Callable[..., Group],
        user_function: Callable[..., User]
) -> None:
    """
    Check whether the function returns correct permissions of the user
    while user belongs to some groups and has directly assigned permissions.

    :param sdk_client: SDK client.
    :param group_function: Group fixture.
    :param user_function: User fixture.

    :return: No return.
    """
    group_1_permissions = ['CREATE', 'GET', 'DELETE']
    group_2_permissions = ['UPDATE', 'GET']
    user_permissions = ['DELETE', 'GET']

    permissions = list(set(group_1_permissions + group_2_permissions + user_permissions))

    # Create groups with some permissions.
    group_1 = group_function(group_1_permissions)
    group_2 = group_function(group_2_permissions)

    # Create user with those permissions.
    user = user_function(permissions=user_permissions, group_ids=[group_1.group_id, group_2.group_id])

    user_permissions = sdk_client.user.permissions(user.username)

    assert sorted(user_permissions) == sorted(permissions), user_permissions
