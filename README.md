# service
API service and prototype

#Set-up 
Install virtual environment using pip
```pip install virtual env```

Install heroku toolbelt
```brew install heroku-toolbelt```

create a virtual environment
```virtualenv venv```
you can call it whatever you want but if you call it venv, then 
.gitignore is already updated for you =] 

In your new virtual environment, clone this repository
```git clone https:THIS-REPOS-URL```

create a local postgres database in psql
``` CREATE DATABASE "database_name" with owner owner_name;
\connect database_name ```

Then set these environment variables in your virtual environment
activate file
``` nano venv/bin/activate ```
``` export APP_SETTINGS = 'config.DevelopmentConfig'
 export DATABASE_URL = 'postgres://owner_name@localhost/database_name' ```

login heroku
``` heroku login ```

In your git repo, add git remote to heroku 
``` heroky git:remote -a atos-service ```


