import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User

@pytest.mark.django_db
def test_signup_success():
    client = APIClient()
    url = reverse('signup')

    data = {
        "email": "newuser@example.com",
        "password": "@Newpassword123",
        "first_name": "New",
        "last_name": "User"
    }

    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email="newuser@example.com").exists()

@pytest.mark.django_db
def test_signup_weak_password():
    client = APIClient()
    url = reverse('signup')

    data = {
        "email": "newuser@example.com",
        "password": "weak",
        "first_name": "New",
        "last_name": "User"
    }

    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'password' in response.data

@pytest.mark.django_db
def test_signup_missing_required_field():
    client = APIClient()
    url = reverse('signup')

    data = {
        "email": "newuser@example.com",
        "password": "@Newpassword123",
        # "first_name": "New",  # Campo obrigatório ausente
        "last_name": "User"
    }

    response = client.post(url, data, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'first_name' in response.data