from faker import Faker

from authena_python_sdk.client import Client


def test_FUNC_client_user_create_WITH_valid_user_attributes_EXPECT_user_created(
        sdk_client: Client,
        faker: Faker
) -> None:
    """
    Check whether a new user can be created.

    :param sdk_client: Authena SDK client fixture.
    :param faker: Faker fixture.

    :return: No return.
    """
    user = sdk_client.user.create(
        email=faker.email(),
        preferred_username=faker.user_name(),
        first_name=faker.first_name(),
        last_name=faker.last_name()
    )

    assert user.is_active, user

    sdk_client.user.delete(user.username)


def test_FUNC_client_user_create_WITH_predefined_username_EXPECT_user_created(
        sdk_client: Client,
        faker: Faker
) -> None:
    """
    Check whether a new user can be created.

    :param sdk_client: Authena SDK client fixture.
    :param faker: Faker fixture.

    :return: No return.
    """
    username = faker.uuid4()

    user = sdk_client.user.create(
        username=username,
        email=faker.email(),
        preferred_username=faker.user_name(),
        first_name=faker.first_name(),
        last_name=faker.last_name()
    )

    assert user.username == username, user

    sdk_client.user.delete(user.username)
