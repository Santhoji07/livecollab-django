# MyChat - Video Chat Web Application using Django

## Project Overview

**MyChat** is a web application that enables users to engage in real-time video chats using Django as the backend framework. The application focuses on providing a seamless and interactive communication experience, making it ideal for personal or professional use.

# Working with Virtual Environments on Your Local Machine

1. Ensure `pip` is installed on your device. The latest version can be installed and upgraded by using the command:
    ```bash
    py -m pip install --upgrade pip
    ```

2. Python uses `venv` as the preferred module to create and manage virtual environments. `venv` is included in the Python standard library and does not require any additional installation. You can create a virtual environment in the specific project directory by running the command:
    ```bash
    py -m venv env
    ```
    *(Here, `env` is the name assigned to the virtual environment, and you can use any name you wish.)*

3. Activate the virtual environment:  
   You need to activate the virtual environment. This will put the virtual environment-specific Python and `pip` executables into your shell’s PATH. You can do this by running the command:
    ```bash
    .\env\Scripts\activate
    ```

    If an error occurs, you can resolve it temporarily by running:
    ```bash
    Set-ExecutionPolicy RemoteSigned -Scope Process
    ```

    To remove the error permanently, run:
    ```bash
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```

4. Exit the virtual environment:  
   You can exit the virtual environment by running the command:
    ```bash
    deactivate
    ```

# Installing Django and Creating a Project

2. To install Django, use the command in the terminal:
    ```bash
    pip install django
    ```

   To check the version of Django, run:
    ```bash
    python -m django --version
    ```

3. To create a project in Django, use:
    ```bash
    django-admin startproject demoproject
    ```
    *(Here, `demoproject` is the name of the project, and you can use any name you wish.)*

   To create the project in the current working directory (avoiding subdirectories with the same name), run:
    ```bash
    django-admin startproject demoproject .
    ```

   Use `CTRL + C` to stop the server, and then deactivate the virtual environment.

# Creating an App and Running Your Django Project

4. The `startapp` command option of the `manage.py` script creates a default folder structure for the app of that name. Here’s how to create a `demoapp` in the `demoproject` folder:
    ```bash
    python manage.py startapp demoapp
    ```

5. To run and view your Django app in the browser, execute the following commands in the terminal:
    - To run the server (if there is more than one Django project):
        ```bash
        django-admin runserver
        ```
    - To run the server (if there is only one Django project):
        ```bash
        python manage.py runserver
        ```

    - To compile the migrations:
        ```bash
        python manage.py makemigrations
        ```

    - To migrate the changes in the database:
        ```bash
        python manage.py migrate
        ```

# Installing MySQL and Configuring Django

1. **Install MySQL**  
   Follow the wizard-based installation steps. First, open a command line terminal, then start the MySQL command line client with the following command:
    ```bash
    mysql -u root -p
    ```
   You will be prompted to enter the password set at the time of installation. In the command terminal, you will get the MySQL prompt where you can enter any SQL statement.

   Start by creating a database with the following command:
    ```sql
    CREATE DATABASE mydatabase;
    ```
   The command `SHOW DATABASES;` will show the list of currently available databases.

2. **Install MySQL DB API Driver**  
   To interface a Python program with MySQL, ensure you have a DB API-compliant driver. Django recommends `mysqlclient`. Install it with:
    ```bash
    pip3 install mysqlclient
    ```

3. **Enable MySQL**  
   To use MySQL, the `DATABASES` variable in the Django project’s settings file must be properly configured. By default, it is set to the connection parameters for SQLite. Remove those statements and add MySQL-specific settings. You must configure at least one database in the `DATABASES` variable, named 'default'. The settings include the database engine, name of the database, username, password, and host IP address (defaults to `127.0.0.1` and port `3306`).

   **Settings.py**
   ```python
   DATABASES = {   
       'default': {   
           'ENGINE': 'django.db.backends.mysql',   
           'NAME': 'mydatabase',   
           'USER': 'root',   
           'PASSWORD': '',   
           'HOST': '127.0.0.1',   
           'PORT': '3306',   
           'OPTIONS': {   
               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"   
           }   
       }   
   }

# Optional Parameters and Creating Database Tables

Other optional parameters include:
- `sql_mode`: The session SQL mode will be set to the given string. Defaults to `STRICT_TRANS_TABLES`.
- `default-character-set`: The character set to be used. Default is `utf8`.
- `read_default_file`: MySQL configuration file to read.
- `init_command`: Initial command to issue to the server upon connection.

## Create Database Tables

The `startproject` template installs some Django apps by default, such as admin, auth, and sessions. You need to create the necessary database tables for these apps. Run the migrate command to build their respective table structure in the current MySQL database:
```bash
python manage.py migrate
```

## Viewing Tables in MySQL

Inside the MySQL terminal, run the following commands:
```sql
USE mydatabase; 
SHOW TABLES;
```

This shows all the tables created by the migration. Instead of viewing the data in the MySQL terminal, you can add a MySQL extension from the VS Code extension library.

## VS Code Extension for MySQL

From the VS Code extension marketplace, search for MySQL and install the extension. MySQL will appear in the explorer.

Click on the `+` button and enter the following details:
- Domain name: `localhost`
- User: `root`
- Password: `'admin'`

**Note**: Some users may encounter an error such as:
*Client does not support authentication protocol requested by server; consider upgrading MySQL client.*  
This usually indicates a user privilege issue. In such cases, first run:
```sql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';
```

Then refresh privileges by running:
```sql
FLUSH PRIVILEGES;
```

Now, the localhost should appear in the explorer. Expand the section by selecting the drop-down arrow and choose mydatabase. All the tables required for the INSTALLED_APPS will be visible.

# Django Rest Framework (DRF)

After creating a virtual environment and setting up a Django project and app for an API:

1. **To install Django Rest Framework (DRF)**:
    ```bash
    pip install djangorestframework
    ```

2. **In the Django project `settings.py`**, add `'rest_framework'` to `INSTALLED_APPS`:
    ```python
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework'
    ]
    ```

3. **Creating an endpoint**:  
   To create an endpoint, go to the app's `views.py` file and write the following code:
    ```python
    from django.shortcuts import render
    from rest_framework.response import Response
    from rest_framework import status
    from rest_framework.decorators import api_view

    # Create your views here.

    @api_view()
    def books(request):
        return Response('list of the books', status=status.HTTP_200_OK)
    ```

4. **To map the above method in the view to an API endpoint**, create a `urls.py` file in the app and write the following code:

    ```python
    from django.urls import path
    from . import views

    urlpatterns = [
        path('book/', views.books),
    ]
    ```

    **Include it in the project's `urls.py` file**:
    ```python
    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('api/', include('your_app_name.urls')),  # Replace 'your_app_name' with the actual app name
    ]
    ```

# Django Admin
## Superuser:
```bash
Username: Admin  
Password: admin123
```

# Djoser
**Djoser** is a Django library that simplifies user authentication by providing a set of easy-to-use RESTful endpoints for common user operations like login, registration, password reset, and token management. It works seamlessly with Django Rest Framework (DRF) and integrates well with JSON Web Tokens (JWT) for secure authentication.

## Installation and Setup

1. **To install Djoser**:
    ```bash
    pip install djoser
    ```

2. **Install Django Rest Framework (DRF)** (if not already installed):
    ```bash
    pip install djangorestframework
    ```

3. **Add `djoser` and `rest_framework` to `INSTALLED_APPS`** in `settings.py`:
    ```python
    INSTALLED_APPS = [
        'rest_framework',
        'djoser',
    ]
    ```

4. **Set up Djoser URLs** in your `urls.py`:
    ```python
    from django.urls import path, include

    urlpatterns = [
        path('auth/', include('djoser.urls')),
        path('auth/', include('djoser.urls.jwt')),  # If using JWT authentication
    ]
    ```

5. **Configure Authentication** in `settings.py` (Optional - For JWT):
    ```python
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        ),
    }

    SIMPLE_JWT = {
        'AUTH_HEADER_TYPES': ('Bearer',),
    }
    ```

6. **Install Simple JWT** (for JWT token-based authentication):
    ```bash
    pip install djangorestframework-simplejwt
    ```

7. **Run migrations** to create necessary database tables:
    ```bash
    python manage.py migrate
    ```
