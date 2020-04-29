*****This repository is obsolete.  Please use the repository located at  http://github.com/helxplatform/appstore for any future development related to AppStore.***** 

# CommonsShare_AppStore

To run locally, follow the steps:

1) Clone the repository:

git clone https://github.com/heliumdatacommons/CommonsShare_AppStore.git

2) Navigate to the root directory:

```
CommonsShare_AppStore/              - root 
├── CS_AppsStore/                   - Project root
    ├── CS_AppsStore/               - Django root
    │   ├── ```__init__.py```
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── manage.py
```

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

5) To install a new app, follow the steps below:

- Navigate to the Project root and run the following command:

    ```python manage.py startapp [app_name]```

- Update CS_AppsStore/settings.py to add your app into INSTALLED_APPS list and add any other app specific settings as needed. Refer to how existing apps such as pivot_hail and phenotype apps are set up there.

- Add an app specific url pattern into CS_AppsStore/urls.py for better encapsulation. Follow the example done for PIVOT HAIL app as shown below:
    ```
    url('^pivot_hail/', include('pivot_hail.urls')),
    ```
- Create apps.py and ```__init__.py``` to have app-specific custom name, verbose_name, url and logo fields populated in AppConfig subclass. Refer to existing apps such as pivot_hail and phenotype apps to see how this is done. The custom verbose_name, url, and logo fields are used to dynamically populate the added apps to apps page for invocation of the app without need for specific coding.

6) Run the following commands to make sure database migration has taken place and all static files have been collectioned to the server:

```python manage.py migrate```

```python manage.py collectstatic```


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

# Docker Development
## Dockerize Django, multiple Postgres databases, NginX, Gunicorn, virtualenv.
- The Django application is served by Gunicorn (WSGI application).
- We use NginX as reverse proxy and static files server. Static files persistently stored in volumes.
- Multiple Postgres databases can be used. Data are persistently stored in volumes.
- Python dependencies are managed through virtualenv.

## Requirements
- Install Docker and Docker-Compose

  [Docker CE for Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
  
  ```sudo apt-get install docker-compose```
- Include the local_settings.py in the CS_AppStore directory.
- Include the pivot_hail.json in the pivot_hail/data/ directory.
- Modify the local_settings.py,


    ```DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'database1',
            'USER': 'postgres',
            'PASSWORD': '<password>',
            'HOST': 'database1',  # <-- IMPORTANT: same name as docker-compose service!
            'PORT': '5432',
        },
        'Backup': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'database2',
            'USER': 'postgres',
            'PASSWORD': '<password>',
            'HOST': 'database2',  # <-- IMPORTANT: same name as docker-compose service!
            'PORT': '5432',
        },
    }
    ```
    The passwords set here 
- Add the IP-Address to the list of Allowed Hosts.
    
## Build the image and run the containers
```sudo docker-compose up -d --build```

## To check the logs
```sudo docker-compose logs -f```

## To update the configuration for NginX and PostgreSql
The configuration files are available in config/ directory.

## Note
This Django project is not SSL-enabled

