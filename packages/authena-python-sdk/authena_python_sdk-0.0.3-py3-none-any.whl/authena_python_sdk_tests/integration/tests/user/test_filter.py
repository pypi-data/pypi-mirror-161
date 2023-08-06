from typing import Callable

from authena_python_sdk.client import Client
from authena_python_sdk.models.group import Group
from authena_python_sdk.models.user import User


def test_FUNC_client_user_filter_WITH_many_users_to_filter_all_EXPECT_users_found(
        sdk_client: Client,
        user_function: Callable[..., User]
) -> None:
    """
    Check whether all users can be retrieved.

    :param sdk_client: SDK client.
    :param user_function: User fixture.

    :return: No return.
    """
    # Create some random users.
    users = [user_function().username for _ in range(10)]

    # Try to filter all users.
    user_data = sdk_client.user.filter()

    # Check that all users were found.
    for username in users:
        assert user_data[username].username == username


def test_FUNC_client_user_filter_WITH_many_users_to_filter_by_usernames_EXPECT_users_found(
        sdk_client: Client,
        user_function: Callable[..., User]
) -> None:
    """
    Check whether the specific users can be filtered.

    :param sdk_client: SDK client.
    :param user_function: User fixture.

    :return: No return.
    """
    # Create some random users.
    for _ in range(10):
        user_function()

    # Create 2 more users and try to find them.
    user_1 = user_function()
    user_2 = user_function()

    # Try to find two users.
    user_data = sdk_client.user.filter(
        usernames=[user_1.username, user_2.username]
    )

    # Check that both users were found.
    assert user_data[user_1.username].username == user_1.username
    assert user_data[user_2.username].username == user_2.username


def test_FUNC_client_user_filter_WITH_many_users_to_filter_by_group_id_EXPECT_users_found(
        sdk_client: Client,
        group_function: Callable[..., Group],
        user_function: Callable[..., User]
) -> None:
    """
    Check whether the users assigned to the specific group can be filtered.

    :param sdk_client: SDK client.
    :param group_function: Group fixture.
    :param user_function: User fixture.

    :return: No return.
    """
    groups_a = [group_function().group_id for _ in range(5)]
    groups_b = [group_function().group_id for _ in range(5)]

    # Create users in group A.
    for _ in range(10):
        user_function(group_ids=groups_a)

    # Create users in group B.
    for _ in range(10):
        user_function(group_ids=groups_b)

    group_filter = groups_a[0]
    # Search by group id.
    user_data = sdk_client.user.filter(
        group_id=group_filter
    )

    # Check that all found users belong to that group.
    for username, user in user_data.items():
        assert group_filter in user.group_ids


def test_FUNC_client_user_filter_WITH_many_users_to_filter_by_usernames_and_group_id_EXPECT_users_found(
        sdk_client: Client,
        group_function: Callable[..., Group],
        user_function: Callable[..., User]
) -> None:
    """
    Check whether filter users by the given usernames and group_id works as expected.

    :param sdk_client: SDK client.
    :param group_function: Group fixture.
    :param user_function: User fixture.

    :return: No return.
    """
    group_a = group_function([])
    group_a_id = group_a.group_id

    group_b = group_function([])
    group_b_id = group_b.group_id

    # Create users in group A.
    for _ in range(10):
        user_function(group_ids=[group_a_id])

    # Create users in group B.
    for _ in range(10):
        user_function(group_ids=[group_b_id])

    # Create 2 more users in group A and try to find them.
    user_a_1 = user_function(group_ids=[group_a_id])
    user_a_1_username = user_a_1.username

    user_a_2 = user_function(group_ids=[group_a_id])
    user_a_2_username = user_a_2.username

    # Search for users by username and group id.
    user_data = sdk_client.user.filter(
        group_id=group_a_id,
        usernames=[user_a_1_username, user_a_2_username]
    )

    # Ensure two users were found.
    assert user_data[user_a_1_username].username == user_a_1_username
    assert group_a_id in user_data[user_a_1_username].group_ids
    assert user_data[user_a_2_username].username == user_a_2_username
    assert group_a_id in user_data[user_a_2_username].group_ids

    user_data = sdk_client.user.filter(
        group_id=group_b_id,
        usernames=[user_a_1_username, user_a_2_username]
    )

    # Ensure no users were found because they belong to a different group.
    assert user_data == {}


def test_FUNC_client_user_filter_WITH_many_users_to_filter_only_active_EXPECT_active_users_found(
        sdk_client: Client,
        user_function: Callable[..., User]
) -> None:
    """
    Check whether only active users can be filtered.

    :param sdk_client: SDK client.
    :param user_function: User fixture.

    :return: No return.
    """
    # Create some random users.
    users = [user_function().username for _ in range(10)]

    # Disable some users.
    user_inactive, users_active = users[:3], users[3:]
    [sdk_client.user.disable(user) for user in user_inactive]
    # Try to filter only active users.
    user_data = sdk_client.user.filter(is_active=True)

    # Check that only active users were found.
    for username in users_active:
        assert user_data[username].username == username
        assert user_data[username].is_active
