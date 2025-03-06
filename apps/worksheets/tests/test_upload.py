import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import pandas as pd
from io import BytesIO
from rest_framework_simplejwt.tokens import RefreshToken
from apps.worksheets.models import Worksheet, WorksheetLine
from apps.worksheets.constants import RequiredColumns


@pytest.fixture
def user_commmon():
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

@pytest.mark.django_db
def create_in_memory_xlsx(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

@pytest.mark.django_db
def test_unauthenticated_request(user_commmon):

    client = APIClient()
    # refresh = RefreshToken.for_user(userCommmon)
    # token = str(refresh.access_token)

    url = f'/worksheets/upload-service/'


    response = client.post(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_regular_user_request(user_commmon):
    client = APIClient()
    refresh = RefreshToken.for_user(user_commmon)
    token = str(refresh.access_token)

    url = f'/worksheets/upload-service/'


    response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_invalid_file_format(staff_user):

    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    invalid_file = BytesIO(b"dummy")
    invalid_file.name = "file.csv"

    url = f'/worksheets/upload-service/'
    data = {'file': invalid_file, 'upload_type': 'test'}
    response = client.post(url, HTTP_AUTHORIZATION=f'Bearer {token}', data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Formato de arquivo inválido' in str(response.data['file'])

@pytest.mark.django_db
def test_missing_columns(staff_user, monkeypatch):

    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    monkeypatch.setattr(RequiredColumns, 'get', lambda x: {'field1': 'col1', 'field2': 'col2'})

    df = pd.DataFrame({'col1': ['data']})
    xlsx_file = create_in_memory_xlsx(df)
    xlsx_file.name = 'file.xlsx'

    data = {'file': xlsx_file, 'upload_type': 'test'}

    url = '/worksheets/upload-service/'
    response = client.post(url, data, format='multipart', HTTP_AUTHORIZATION=f'Bearer {token}')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Colunas faltantes' in response.data['message']

@pytest.mark.django_db
def test_successful_upload(staff_user, monkeypatch):
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    token = str(refresh.access_token)

    monkeypatch.setattr(RequiredColumns, 'get', lambda x: {'field1': 'col1', 'field2': 'col2'})
    client.force_authenticate(user=staff_user)

    df = pd.DataFrame({'col1': ['data1'], 'col2': ['data2']})
    xlsx_file = create_in_memory_xlsx(df)
    xlsx_file.name = 'file.xlsx'

    url = f'/worksheets/upload-service/'
    data = {'file': xlsx_file, 'upload_type': 'test'}


    response = client.post(url, data, format='multipart', HTTP_AUTHORIZATION=f'Bearer {token}')


    assert response.status_code == status.HTTP_201_CREATED
    assert Worksheet.objects.count() == 1
    assert WorksheetLine.objects.count() == 1
