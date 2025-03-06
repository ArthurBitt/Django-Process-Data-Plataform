from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

import pytest

@pytest.fixture
def user():
    return get_user_model().objects.create_user(
        email='testuser1@example.com',
        username='testuser1',
        password='password123',
        is_active=True,
    )
@pytest.fixture
def staff():
    return get_user_model().objects.create_user(
        email='testuser2@example.com',
        username='testuser1',
        password='password123',
        is_active=True,
        is_staff = True
    )
@pytest.mark.django_db
def test_list_users_not_staff_or_admin(user):
    """Testa login com credenciais corretas"""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)

    url = '/users/users-list-service/'

    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == 403

@pytest.mark.django_db
def test_list_users(staff):
    """Testa login com credenciais corretas"""
    client = APIClient()
    refresh = RefreshToken.for_user(staff)
    token = str(refresh.access_token)

    url = '/users/users-list-service/'

    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == 200
    assert 'results' in response.data
    if not response.data['results']:
        assert response.data['message'] == 'No users found'