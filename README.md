[![Build Status](https://travis-ci.org/ucl-team-8/service.svg?branch=CI)](https://travis-ci.org/ucl-team-8/service)

# Setting up local environment

Install virtual environment using pip

```
pip install virtualenv
```

create a virtual environment

```
virtualenv venv
```

In your new virtual environment, clone this repository

```
git clone https://github.com/ucl-team-8/service.git
```

Create a local postgres database with `psql`

```
CREATE USER atos WITH PASSWORD 'atos';
CREATE DATABASE atos WITH OWNER atos;
GRANT ALL PRIVILEGES ON DATABASE atos TO atos;
```

Then run these bash commands to set the environment variables in your virtual environment `activate` file

```
echo "export APP_SETTINGS='config.DevelopmentConfig'" >> venv/bin/activate
echo "export DATABASE_URL='postgres://atos:atos@localhost/atos'" >> venv/bin/activate
```

activate your virtual environment

```
source venv/bin/activate
```

install requirements from requirements.txt

```
pip install -r requirements.txt
```


## Updating database

Since the migration files are included in the repo, when updating the models, include the migration script and other collaborators just run

```
python manage.py db upgrade
```

once the latest version of the repo is pulled


## Installing visualisation dependencies

`cd` to the project folder and run

```
brew install node
npm install -g jspm
npm install
jspm install
```


# Setting up production

Install heroku toolbelt

```
brew install heroku-toolbelt
```

Log into heroku

```
heroku login
```

In your git repo, add git remote to heroku

```
heroku git:remote -a atos-service
```

Whenever you want to push to production, run:

```
git push heroku master
```
