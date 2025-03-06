import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from apps.worksheets.models import Worksheet, WorksheetLine
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

@pytest.fixture
def user_common():
    return get_user_model().objects.create_user(
        email='testuser1@example.com',
        username='testuser1',
        password='password123',
        is_active=True
    )

@pytest.fixture
def staff_user():
    return get_user_model().objects.create_user(
        email='testuser2@example.com',
        username='staff_user',
        password='password123',
        is_active=True,
        is_staff=True
    )

@pytest.fixture
def worksheet(staff_user):
    worksheet = Worksheet.objects.create(created_by=staff_user)
    WorksheetLine.objects.create(worksheet_id=worksheet, data={'column1': 'value1', 'column2': 'value2'})
    return worksheet

@pytest.mark.django_db
def test_download_report_valid(staff_user, worksheet):

    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)
    url = f'/worksheets/download-excel-report-service/{worksheet.id}/'

    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_200_OK
    assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    assert response['Content-Disposition'] == f'attachment; filename="planilha_{worksheet.id}.xlsx"'

@pytest.mark.django_db
def test_download_report_invalid_id(staff_user):

    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)


    invalid_uuid = '00000000-0000-0000-0000-000000000000'
    url = f'/worksheets/download-excel-report-service/{invalid_uuid}/'

    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'worksheet_id' in str(response.data)

@pytest.mark.django_db
def test_download_report_unauthenticated(worksheet):
    client = APIClient()
    url = f'/worksheets/download-excel-report-service/{worksheet.id}/'
    response = client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_download_report_unauthorized(user_common, worksheet):
    client = APIClient()
    refresh = RefreshToken.for_user(user_common)

    token = str(refresh.access_token)
    url = f'/worksheets/download-excel-report-service/{worksheet.id}/'
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')
    assert response.status_code == status.HTTP_403_FORBIDDEN