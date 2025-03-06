from django.contrib.auth import get_user_model
import pytest
import uuid

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# Define the fixtures using @pytest.fixture
@pytest.fixture
def userActive():
    return get_user_model().objects.create_user(
        email='testuser1',
        username ='testuser1',
        password='password123',
        is_active=True
    )

@pytest.fixture
def userInactive():
    return get_user_model().objects.create_user(
        email='testuser2',
        username='testuser2',
        password='password123',
        is_active=False
    )


@pytest.mark.django_db
def test_inactivate_user(userActive):
    client = APIClient()

    refresh = RefreshToken.for_user(userActive)
    token = str(refresh.access_token)

    url = f'/users/user-inactivate-service/{userActive.id}/'

    response = client.delete(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.data == {'message': 'User sucessfully inactivated!'}

    userActive.refresh_from_db()
    assert not userActive.is_active

@pytest.mark.django_db
def test_inactivate_user_not_found(userActive):
    client = APIClient()
    refresh = RefreshToken.for_user(userActive)
    token = str(refresh.access_token)

    invalid_uuid = uuid.uuid4()
    url = f'/users/user-inactivate-service/{invalid_uuid}/'

    response = client.delete(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'][0] == 'User not found'

@pytest.mark.django_db
def test_inactivate_user_already_inactivated(userActive, userInactive):
    client = APIClient()

    refresh = RefreshToken.for_user(userActive)
    token = str(refresh.access_token)
    # obs. usuarios inativos nao podem logar nem receber tokens

    url = f'/users/user-inactivate-service/{userInactive.id}/'

    response = client.delete(url, HTTP_AUTHORIZATION=f'Bearer {token}')
    print(response.data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'][0] == 'User already inactivated'
    userActive.refresh_from_db()
    assert not userInactive.is_active