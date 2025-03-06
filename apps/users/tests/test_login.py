from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse

import pytest

@pytest.fixture
def user():
    return get_user_model().objects.create_user(
        email='testuser1@example.com',
        username='testuser1',
        password='password123',
        is_active=True
    )

@pytest.mark.django_db
def test_login_success(user):
    """Testa login com credenciais corretas"""
    client = APIClient()
    url = reverse('login')

    # Dados de login corretos
    data = {
        "email": user.email,
        "password": "password123"
    }

    response = client.post(url, data, format='json')

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data

@pytest.mark.django_db
def test_login_wrong_password(user):
    """Testa login com senha incorreta"""


    client = APIClient()
    url = reverse('login')

    data = {
        "email": user.email,
        "password": "password1234"
    }

    response = client.post(url, data, format='json')

    assert response.status_code == 401
    assert response.data["message"] == "Invalid credentials"

@pytest.mark.django_db
def test_login_user_not_found(user):
    """Testa login com e-mail não cadastrado"""
    client = APIClient()
    url = reverse('login')

    data = {
        "email": 'emailnotfound@email.com',
        "password": "password1234"
    }

    response = client.post(url, data, format='json')

    assert response.status_code == 401
    assert response.data["message"] == "Invalid credentials"

@pytest.mark.django_db
def test_login_user_inactivated(user):
    """Testa login com usuário inativado"""
    client = APIClient()
    url = reverse('login')

    # Desativa o usuário
    user.is_active = False
    user.save()

    # Dados de login corretos (mas o usuário está inativo)
    data = {
        "email": user.email,
        "password": "password123"
    }

    response = client.post(url, data, format='json')

    assert response.status_code == 401
    assert response.data["message"] == "User is inactive"