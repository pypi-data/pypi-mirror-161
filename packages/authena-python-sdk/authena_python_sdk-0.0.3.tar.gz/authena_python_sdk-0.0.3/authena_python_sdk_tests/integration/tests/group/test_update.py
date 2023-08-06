from time import sleep
from typing import Callable

from faker import Faker

from authena_python_sdk.client import Client
from authena_python_sdk.models.group import Group


def test_FUNC_client_group_update_WITH_valid_configuration_EXPECT_group_updated(
        sdk_client: Client,
        group_function: Callable[..., Group],
        faker: Faker
) -> None:
    """
    Check whether with good configuration a group can be updated.

    :param sdk_client: Authena SDK client.
    :param group_function: Function, that creates group entity.
    :param faker: Faker fixture.

    :return: No return.
    """
    # Create a group with no permissions.
    group = group_function([])

    # Make sure that the group was created and indeed it has no permissions.
    assert group.permissions == [], group.permissions

    new_permissions = ['CREATE', 'GET', 'DELETE']
    new_group_name = faker.word()

    sdk_client.group.update(
        group_id=group.group_id,
        group_name=new_group_name,
        permissions=new_permissions
    )
    # Sleep for the cache to be cleared.
    sleep(11)

    updated_group = sdk_client.group.get(group_id=group.group_id)

    assert updated_group.group_id == group.group_id, updated_group.group_id
    assert updated_group.group_name == new_group_name, updated_group.group_name
    assert sorted(updated_group.permissions) == sorted(new_permissions), updated_group.permissions
