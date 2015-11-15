# service
API service and prototype

# Set-up

Install virtual environment using pip

```
pip install virtualenv
```

Install heroku toolbelt

```
brew install heroku-toolbelt
```

create a virtual environment

```
virtualenv venv
```

In your new virtual environment, clone this repository

```
git clone https://github.com/ucl-team-8/service.git
```

create a local postgres database in psql

```
CREATE USER atos WITH PASSWORD 'atos';
CREATE DATABASE atos WITH OWNER atos;
GRANT ALL PRIVILEGES ON DATABASE atos TO atos;
```

Then set these environment variables in your virtual environment
activate file

```
echo "export APP_SETTINGS='config.DevelopmentConfig'" >> venv/bin/activate
echo "export DATABASE_URL = 'postgres://atos:atos@localhost/atos'" >> venv/bin/activate
```

login heroku

```
heroku login
```

In your git repo, add git remote to heroku

```
heroky git:remote -a atos-service
```
