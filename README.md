# Project Documentation

## Lead Developer
**Name:** [Arthur Bittencourt](https://github.com/ArthurBitt) 

## Project Summary
This project is a Django application designed to manage customer data processing through spreadsheets (worksheets). It provides a basic user CRUD and includes features such as:

- **File Upload:** Allows users to upload spreadsheets for processing.
- **Worksheet Reprocessing:** Enables reprocessing of previously uploaded worksheets.
- **Excel Report Generation:** Generates reports from processed data.
- **Celery Integration:** Uses asynchronous tasks for background processing.

The project is built as a modular base, allowing new projects to integrate with the automation app, leveraging existing configurations and functionalities. It is not a definitive solution but a flexible structure that can be expanded and adapted as needed.

## Requirements
- Python >= 3.10
- Celery >= 5.4.0
- Redis [Docker Redis Image](https://hub.docker.com/_/redis)
- Django >= 5.1.6
- Pandas >= 2.2.3

## Environment Configuration - DEBUG

```bash
# Clone the project repository
mkdir django-rpa-core
git clone <project-repository-url>
```

```bash
# Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Environment Settings
```bash
# DJANGO CONFIGS
DEBUG= # Controls the application mode in settings.py
CORS_ALLOWED_ORIGINS= # Configures allowed CORS origins in settings.py
CSRF_TRUSTED_ORIGINS=
ALLOWED_HOSTS= # Controls permitted hosts

# SELENIUM CONFIGS
EXECUTE_WITH_REMOTE_WEB_DRIVER="False" # Runs Selenium locally
REMOTE_WEB_DRIVER=""

# CONFIG BROKER
REDIS_URL="" # Redis broker configuration

# LIMIT ROBOT
LIMIT_ROBOT=10 # Rate limit to process only 10 records at a time

# SLEEPING PARAMS
SLEEPING_PARAMS = '3,20,4' # Prevents concurrent tasks

# EMAIL(Credentials must be requested from the admin)
EMAIL_TO=
MAIL_TOKEN=
ENDPOINT_MAIL=
ID_TEMPLATE_COMPLETED_WORKSHEET=

# DATABASE CONFIG
DATABASE_URL='' # Database configuration when NOT in debug mode

# TEMP DIR - Handles export and download of temporary files
DIRECTORY = # Path for report creation, deleted after download or email dispatch
```

### Database Configuration
#### DEBUG Mode (SQLite)
```bash
DEBUG = True  # Uses SQLite as default database
```

#### Production Example (PostgreSQL)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'database_name',
        'USER': 'database_user',
        'PASSWORD': 'database_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Installing Dependencies
```bash
pip install -r requirements.txt
```

## Running Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Running Tests
```bash
pytest -v
```

# Features

## Automations
- **[config/] Custom Selenium Driver:** Provides a custom Selenium WebDriver with pre-configured functions for automation and task handling.
- **[automation/constants.py] Tag Mapping:** Organizes the construction of HTML paths.
- **[utils/enums.py] ProcessingStatus | AutomationErrorStatus:** Provides functions for error handling and task status configurations.

## User Management

### User Levels
- **Common User:** Neither staff nor superuser.
- **Staff User:** Staff=True.
- **Superuser:** is_superuser=True.
- **Admin:** Must be both staff and superuser.

### Actions
- **User Registration:** Allows new users to sign up.
- **User Login:** Authenticates users and provides JWT tokens.
- **User Listing:** Lists all users (staff/admin only).
- **User Update:** Updates user information (staff/admin only).
- **User Inactivation:** Deactivates a user (staff/admin only).
- **User Activation:** Reactivates a user (staff/admin only).
- **Password Recovery (in development):** Sends a password recovery email.

## Worksheets
- **Upload Worksheet:** Uploads and processes XLSX files.
- **Download Report:** Downloads processed worksheet reports in XLSX format.
- **List Worksheets:** Lists all worksheets with pagination.
- **List Worksheet Lines:** Lists worksheet lines with optional status filtering.
- **Reprocess Worksheet:** Reprocesses lines with errors.
- **Reprocess Lines (in development):** Reprocess individual line with error

# API Endpoints

### User Endpoints
- **POST** `/users/signup-service/` - Register a new user.
- **POST** `/users/login-service/` - Authenticate and receive JWT tokens.
- **GET** `/users/users-list-service/` - List all users (staff/admin only).
- **PUT** `/users/user-update-service/<uuid>/` - Update user information (staff/admin only).
- **DELETE** `/users/user-inactivate-service/<uuid>/` - Deactivate a user (staff/admin only).
- **PUT** `/users/user-activate-service/<uuid>/` - Reactivate a user (staff/admin only).
- **POST** `/users/recover_password-service/` - Initiate password recovery.

### Worksheet Endpoints (staff/admin only)
- **POST** `/worksheets/upload-service/` - Upload and process a worksheet.
- **GET** `/worksheets/download-excel-report-service/<worksheet_id>/` - Download worksheet report.
- **GET** `/worksheets/list-worksheets-service/` - List all worksheets.
- **GET** `/worksheets/list-worksheet-lines-service/<worksheet_id>/` - List worksheet lines.
- **POST** `/worksheets/reprocess-worksheet-service/<worksheet_id>/` - Reprocess worksheet lines.

### Basic Flow
1. **Sign Up:** User registers via `/users/signup-service/`.
2. **Login:** User logs in via `/users/login-service/` and receives JWT tokens.
3. **Token Refresh:** User refreshes tokens via `/token/refresh/`.
4. **Upload Worksheet:** User uploads a worksheet via `/worksheets/upload-service/`.
5. **Process Worksheet:** The system processes the worksheet using Celery tasks.
6. **Download Report:** User downloads the processed report via `/worksheets/download-excel-report-service/<worksheet_id>/`.

---
This document provides a comprehensive guide to setting up, configuring, and utilizing the Django Core RPA system. If you need further enhancements, let me know! 🚀
