from typing import Callable

from faker import Faker

from authena_python_sdk.client import Client
from authena_python_sdk.models.group import Group


def test_FUNC_client_group_filter_WITH_new_group_EXPECT_new_group_found(
        sdk_client: Client,
        group_function: Callable[..., Group],
        faker: Faker
) -> None:
    """
    Test whether filter function works as expected.

    :param sdk_client: Authena SDK client.
    :param group_function: Function, that creates group entity.
    :param faker: Faker fixture.

    :return: No return.
    """
    # Create some groups for filtering.
    group_ids = [group_function().group_id for _ in range(5)]

    filtered_groups = sdk_client.group.filter()

    filtered_group_ids = [key for key in filtered_groups.keys()]

    assert filtered_group_ids
