from faker import Faker

from authena_python_sdk.client import Client


def test_FUNC_client_group_create_WITH_valid_configuration_EXPECT_group_created(sdk_client: Client, faker: Faker) -> None:
    """
    Check whether with good configuration a new group can be created.

    :param sdk_client: Authena SDK client.

    :return: No return.
    """
    group_name = faker.word()
    permissions = []

    group = sdk_client.group.create(
        group_name=group_name,
        permissions=permissions
    )

    assert group.group_name == group_name
    assert group.permissions == permissions

    sdk_client.group.delete(group.group_id)


def test_FUNC_client_group_create_WITH_specific_group_id_EXPECT_group_created(sdk_client: Client, faker: Faker) -> None:
    """
    Check whether a new group with specific group_id can be created.

    :param sdk_client: Authena SDK client.

    :return: No return.
    """
    group_id = faker.uuid4()
    group_name = faker.word()
    permissions = []

    group = sdk_client.group.create(
        group_id=group_id,
        group_name=group_name,
        permissions=permissions
    )
    assert group.group_id == group_id
    assert group.group_name == group_name
    assert group.permissions == permissions

    sdk_client.group.delete(group.group_id)
