import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.worksheets.models import Worksheet, WorksheetLine

@pytest.fixture
def staff_user():
    return get_user_model().objects.create_user(
        email='staff@example.com',
        username='staff_user',
        password='password123',
        is_staff=True
    )
@pytest.fixture
def worksheet(staff_user):
    worksheet = Worksheet.objects.create(created_by=staff_user)
    WorksheetLine.objects.create(
        worksheet_id=worksheet,
        process_status=1,
        data={"key": "value"}  # Adicione um valor para o campo `data`
    )
    WorksheetLine.objects.create(
        worksheet_id=worksheet,
        process_status=4,
        data={"key": "value"}  # Adicione um valor para o campo `data`
    )
    WorksheetLine.objects.create(
        worksheet_id=worksheet,
        process_status=5,
        data={"key": "value"}  # Adicione um valor para o campo `data`
    )
    return worksheet

@pytest.mark.django_db
def test_list_process_data_success(staff_user, worksheet):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    url = '/worksheets/list-worksheets-service/'
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1

    assert str(response.data['results'][0]['worksheet_id']) == str(worksheet.id)
    assert response.data['results'][0]['worksheet_total_lines'] == 3

@pytest.mark.django_db
def test_list_process_data_empty(staff_user):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    url = '/worksheets/list-worksheets-service/'
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['message'] == 'Not found'

@pytest.mark.django_db
def test_list_process_data_multiple_worksheets(staff_user):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    # Cria múltiplas planilhas
    for _ in range(5):
        worksheet = Worksheet.objects.create(created_by=staff_user)
        WorksheetLine.objects.create(worksheet_id=worksheet, process_status=1, data={"key": "value"})

    url = '/worksheets/list-worksheets-service/'
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 5  # Verifica se todas as planilhas são retornadas

@pytest.mark.django_db
def test_list_process_data_unauthenticated():
    client = APIClient()

    url = '/worksheets/list-worksheets-service/'
    response = client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_list_worksheet_lines_success(staff_user, worksheet):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    url = f'/worksheets/list-worksheet-lines-service/{worksheet.id}/'
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3

@pytest.mark.django_db
def test_list_worksheet_lines_with_status_filter(staff_user, worksheet):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    url = f'/worksheets/list-worksheet-lines-service/{worksheet.id}/?status=4'
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['process_status'] == 'processado com sucesso'

@pytest.mark.django_db
def test_list_worksheet_lines_no_status_filter(staff_user, worksheet):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    url = f'/worksheets/list-worksheet-lines-service/{worksheet.id}/'
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3  # Verifica se todas as linhas são retornadas

@pytest.mark.django_db
def test_list_worksheet_lines_invalid_worksheet_id(staff_user):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    invalid_uuid = '00000000-0000-0000-0000-000000000000'
    url = f'/worksheets/list-worksheet-lines-service/{invalid_uuid}/'
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'worksheet not found' in str(response.data)

@pytest.mark.django_db
def test_list_worksheet_lines_invalid_status(staff_user, worksheet):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    url = f'/worksheets/list-worksheet-lines-service/{worksheet.id}/?status=99'
    response = client.get(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Status are between 1 and 5' in str(response.data)
