FROM python:3.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#Switch the working directory.
WORKDIR /usr/src/inst-mgmt

#Install pycopg2 for postgresql.
RUN pip install psycopg2~=2.6

# Install Virtual Environment
RUN pip install --upgrade pip
RUN pip install virtualenv
COPY ./requirements.txt /usr/src/inst-mgmt/requirements.txt
RUN virtualenv /usr/src/inst-mgmt/venv
RUN /bin/bash -c "source /usr/src/inst-mgmt/venv/bin/activate"
RUN pip install -r /usr/src/inst-mgmt/requirements.txt

EXPOSE 8000
EXPOSE 5432
COPY . /usr/src/inst-mgmt

#CMD ["gunicorn", "--bind", ":8000", "CS_AppsStore.wsgi:application"]
