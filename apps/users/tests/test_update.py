import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

User = get_user_model()

@pytest.fixture
def updated_user():
    return User.objects.create_user(
        email='user_to_update@example.com',
        username='user_to_update',
        password='password123',
        is_active=True,
    )

@pytest.fixture
def user():
    return User.objects.create_user(
        email='testuser1@example.com',
        username='testuser1',
        password='password123',
        is_active=True,
    )

@pytest.fixture
def staff():
    return User.objects.create_user(
        email='staffuser@example.com',
        username='staffuser',
        password='password123',
        is_active=True,
        is_staff=True,
    )

@pytest.mark.django_db
def test_update_user_success(staff, user, updated_user):
    client = APIClient()
    refresh = RefreshToken.for_user(staff)
    token = str(refresh.access_token)

    url = f'/users/user-update-service/{updated_user.id}/'

    data = {
        'email': 'updated_email@example.com',
        'first_name': 'Updated',
        'last_name': 'User',
    }

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    response = client.put(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK

    updated_user.refresh_from_db()

    assert updated_user.email == 'updated_email@example.com'
    assert updated_user.first_name == 'Updated'
    assert updated_user.last_name == 'User'

@pytest.mark.django_db
def test_update_user_not_found(staff):
    client = APIClient()
    refresh = RefreshToken.for_user(staff)
    token = str(refresh.access_token)

    non_existent_user_id = '8beeb27270f94aab98b528e97bc581bc'
    url = f'/users/user-update-service/{non_existent_user_id}/'

    data = {
        'email': 'updated_email@example.com',
        'first_name': 'Updated',
        'last_name': 'User',
    }

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    response = client.put(url, data, format='json')

    print(response.data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'][0] == 'User not found'

@pytest.mark.django_db
def test_update_user_not_active(staff, user):
    client = APIClient()
    refresh = RefreshToken.for_user(staff)
    token = str(refresh.access_token)

    user.is_active = False
    user.save()
    url = f'/users/user-update-service/{user.id}/'

    data = {
        'email': 'updated_email@example.com',
        'first_name': 'Updated',
        'last_name': 'User',
    }

    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = client.put(url, data, format='json')
    print(response.data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['detail'][0] == 'This user is not activated'

@pytest.mark.django_db
def test_update_user_unauthorized(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)

    url = f'/users/user-update-service/{user.id}/'

    data = {
        'email': 'updated_email@example.com',
        'first_name': 'Updated',
        'last_name': 'User',
    }


    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = client.put(url, data, format='json')
    print(response.data)

    assert response.status_code == status.HTTP_403_FORBIDDEN

