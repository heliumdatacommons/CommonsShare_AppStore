# CommonsShare_AppStore

To run locally, follow the steps:

1) Clone the repository:

git clone https://github.com/heliumdatacommons/CommonsShare_AppStore.git

2) Navigate to the root directory:

CommonsShare_AppStore/              - root 
├── CS_AppsStore/                   - Project root
    ├── CS_AppsStore/               - Django root
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

    - Since the OAuth service only returns to a web server hosted in commonsshare.org domain for security reasons, oauth-based user authentication has to be bypassed in the local development environment. This can be managed via a configuration variable, but for now, these lines can be commented out to bypass oauth user authentication: <https://github.com/heliumdatacommons/CommonsShare_AppStore/blob/master/CS_AppsStore/CS_Apps/views.py#L21-L25>. In addition, this line <https://github.com/heliumdatacommons/CommonsShare_AppStore/blob/master/CS_AppsStore/templates/base.html#L38> has to be changed to ```<li id="signin-menu"><a href="/accounts/signin/"><span class="glyphicon glyphicon-log-out"></span> Sign In</a></li>``` in order to allow users to sign in.
    - Add an app specific url pattern into CS_AppsStore/urls.py for better encapsulation. Follow the example done for PIVOT HAIL app as shown below:
    ```
    url('^pivot_hail/', include('pivot_hail.urls')),
    ```
    - Update CS_AppsStore/templates/apps.html to add your app to the apps page, following example of other apps.
    - Update CS_AppsStore/settings.py to add your app into INSTALLED_APPS list.
        

# Migrate the project from sqlite to postgreSql.

1) Dump the contents to json

    ```python manage.py dumpdata > dump.json```

2) Switch the db backend in the CS_AppsStore/settings.py

Scroll to the Database section:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db-kyle.sqlite3'),
    }
}
```

change this to,


```DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.posgresql_psycopg2',
        'NAME': '<Name of the DB>',
        'USER': 'postgres',
        'PASSWORD': '<password>',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
```
    
3) Install the required packages in the project virtual environment

    ```apt-get install postgresql-10```

    ```pip install psycopg2-binary```

4) Create a database in the new postgresql DB. 

    ```sudo su - postgres```

    ```psql```

create a password for the postgres user
```
    \password
    CREATE DATABASE <Name of the DB>;
```    

The password here should match the one specified in the CS_AppsStore/settings.py

The DB name should match with the one specified in the CS_AppsStore/settings.py

5) Migrate the new DB to the same table structure

    
    ```python manage.py migrate```
    

6) Load the json to the new DB

    
    ```python manage.py loaddata dump.json```
    

The "dump.json" is created in the Step-1
