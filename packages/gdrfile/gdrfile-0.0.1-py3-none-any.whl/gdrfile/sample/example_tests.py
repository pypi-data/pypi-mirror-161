import pytest
from faker import Faker
from rest_framework import status
from rest_framework.reverse import reverse

fake = Faker()


@pytest.mark.django_db()
def test_{{main_class}}_format(
    api_client,
    {{main_class}},
    {{main_class}}_format,
):
    """Формат {{MainClass}}."""
    url = reverse('{{app-name}}:{{main-class}}-detail', [{{main_class}}.pk])

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response == {{main_class}}_format({{main_class}})


@pytest.mark.django_db()
def test_{{main_class}}_post(
    api_client,
):
    """Создание {{MainClass}}."""
    url = reverse('{{app-name}}:{{main-class}}-list')
    response = api_client.post(
        url,
        data={},
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db()
def test_{{main_class}}_delete(api_client, {{main_class}}):
    """Удаление {{MainClass}}."""
    url = reverse('{{app-name}}:{{main-class}}-detail', [{{main_class}}.pk])

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db()
def test_{{main_class}}_change(
    api_client,
    {{main_class}},
):
    """Изменение {{MainClass}}."""
    url = reverse('api:{{app-name}}:{{main-class}}-detail', [{{main_class}}.pk])

    response = api_client.put(
        url,
        data={},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
