# CommonsShare_AppStore

To run locally, follow the steps:

1) Clone the repository:

git clone https://github.com/heliumdatacommons/CommonsShare_AppStore.git

2) Navigate to the root directory:

CommonsShare_AppStore/      - root 
├── CSv1/                   - Project root
    ├── CSv1/               - Django root
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── manage.py

- Make sure you have virtualenv installed on your system and run the following command to create a virtual environment:

    ```virtualenv venv```

- Activate the virtual environment:

    ```source venv/bin/activate```

- Install the dependencies in the virtual environment:

    ```pip install -r requirements.txt```

3) Navigate to the Django root, modify the settings.py:

Add the IP Address of the local machine to the list of ALLOWED_HOSTS if you are running the Django server on an AWS EC2 instance.

4) Navigate to the Project root and run the Django server:

```python manage.py runserver```

5) To install a new app. Navigate to the Project root and run the following command:

```python manage.py startapp [app_name]```

6) Run the following commands to make sure database migration has taken place and all static files have been collectioned to the server:

```python manage.py migrate```

```python manage.py collectstatic```

7) To develop the new app in your local development environment and get the new app installed in the apps store, follow the steps below:

- Since the OAuth service only returns to a web server hosted in commonsshare.org domain for security reasons, oauth-based user authentication has to be bypassed in the local development environment. This can be managed via a configuration variable, but for now, these lines can be commented out to bypass oauth user authentication: <https://github.com/heliumdatacommons/CommonsShare_AppStore/blob/master/CSv1/CS_Apps/views.py#L21-L25>. In addition, this line <https://github.com/heliumdatacommons/CommonsShare_AppStore/blob/master/CSv1/templates/base.html#L38> has to be changed to ```<li id="signin-menu"><a href="/accounts/signin/"><span class="glyphicon glyphicon-log-out"></span> Sign In</a></li>``` in order to allow users to sign in.
- 



