from django.contrib.auth import get_user_model
import pytest
import uuid

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.fixture
def userActive():
    return get_user_model().objects.create_user(
        email='testuser1@example.com',
        username='testuser1',
        password='password123',
        is_active=True
    )

@pytest.fixture
def userInactive():
    return get_user_model().objects.create_user(
        email='testuser2@example.com',
        username='testuser2',
        password='password123',
        is_active=False
    )

@pytest.mark.django_db
def test_activate_user_success(userInactive, userActive):
    client = APIClient()
    refresh = RefreshToken.for_user(userActive)
    token = str(refresh.access_token)

    url = f'/users/user-activate-service/{userInactive.id}/'

    # Send PUT request to activate the inactive user
    response = client.put(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'message': 'User sucessfully activated!'}

    userInactive.refresh_from_db()
    assert userInactive.is_active  # Now active

@pytest.mark.django_db
def test_activate_user_not_found(userActive):
    client = APIClient()
    refresh = RefreshToken.for_user(userActive)
    token = str(refresh.access_token)

    invalid_uuid = uuid.uuid4()
    url = f'/users/user-activate-service/{invalid_uuid}/'

    # Send PUT request with invalid user ID
    response = client.put(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'][0] == 'User not found'

@pytest.mark.django_db
def test_activate_user_already_activated(userActive):
    client = APIClient()
    refresh = RefreshToken.for_user(userActive)
    token = str(refresh.access_token)

    url = f'/users/user-activate-service/{userActive.id}/'

    # Send PUT request to activate an already active user
    response = client.put(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'][0] == 'User already Activated'

    userActive.refresh_from_db()
    assert userActive.is_active  # Remains active