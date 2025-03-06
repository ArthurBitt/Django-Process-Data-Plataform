import pytest
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
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
def user_common():
    return get_user_model().objects.create_user(
        email='common@example.com',
        username='common_user',
        password='password123',
        is_active=True
    )


@pytest.fixture
def worksheet(staff_user):
    worksheet = Worksheet.objects.create(
        created_by=staff_user,
        process_status=5  # Defina o process_status da planilha
    )
    WorksheetLine.objects.create(
        worksheet_id=worksheet,
        process_status=5,  # Defina o process_status da linha
        data={"key": "value"}
    )
    return worksheet

@pytest.mark.django_db
def test_reprocess_worksheet_success(staff_user, worksheet):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    url = f'/worksheets/reprocess-worksheet-service/{worksheet.id}/'
    response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    # Depuração: Imprima a resposta para identificar o problema
    print(response.data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == "Lines successfully queued for reprocessing"

@pytest.mark.django_db
def test_reprocess_worksheet_invalid_id(staff_user):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    invalid_uuid = '00000000-0000-0000-0000-000000000000'
    url = f'/worksheets/reprocess-worksheet-service/{invalid_uuid}/'
    response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Worksheet not found' in str(response.data)

@pytest.mark.django_db
def test_reprocess_worksheet_no_lines_to_reprocess(staff_user, worksheet):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    # Remove todas as linhas com status 5
    WorksheetLine.objects.filter(worksheet_id=worksheet, process_status=5).delete()

    url = f'/worksheets/reprocess-worksheet-service/{worksheet.id}/'
    response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'There are no lines to reprocess' in str(response.data)

@pytest.mark.django_db
def test_reprocess_worksheet_unauthenticated(worksheet):
    client = APIClient()
    url = f'/worksheets/reprocess-worksheet-service/{worksheet.id}/'
    response = client.post(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_reprocess_worksheet_unauthorized(user_common, worksheet):
    client = APIClient()
    refresh = RefreshToken.for_user(user_common)
    token = str(refresh.access_token)

    url = f'/worksheets/reprocess-worksheet-service/{worksheet.id}/'
    response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_403_FORBIDDEN