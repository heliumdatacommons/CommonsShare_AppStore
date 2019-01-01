# CommonsShare_AppStore

To run locally, follow the steps:

1) Clone the repository:

git clone https://github.com/muralikarthikk/CommonsShare_AppStore.git

2) Navigate to the root directory:

CommonsShare_AppStore/      - root 
├── CSv1/                   - Project root
    ├── CSv1/               - Django root
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    └── manage.py

Activate the virtual environment:

source venv/bin/activate

Install the dependencies:

pip install -r requirements.txt

3) Navigate to the Django root, modify the settings.py:

Add the IP Address of the local machine to the list of ALLOWED_HOSTS if you are running the Django server on an AWS EC2 instance.

4) Navigate to the Project root and run the Django server:

python manage.py runserver

5) To install a new app. Navigate to the Project root and run the following command:

python manage.py startapp [app_name]






