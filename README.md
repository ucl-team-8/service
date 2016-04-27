# Atos Pattern Matching Algorithm [![Build Status](https://travis-ci.org/ucl-team-8/service.svg?branch=master)](https://travis-ci.org/ucl-team-8/service)

To get started, you will need to install [pip](https://pip.pypa.io/en/stable/installing/), [git](https://confluence.atlassian.com/bitbucket/set-up-git-744723531.html), [PostgreSQL](http://www.postgresql.org/download/) (and [brew](http://brew.sh/), if you're using a mac).

## Setting Up the Database

Create a postgres database with `psql` (installed with PostgreSQL):

```
CREATE USER atos WITH PASSWORD 'atos';
CREATE DATABASE atos WITH OWNER atos;
GRANT ALL PRIVILEGES ON DATABASE atos TO atos;
```

## Setting Up a Local Environment

First, you will need to install `virtualenv` using pip:

```
pip install virtualenv
```

After you have virtualenv installed, create a virtual environment:

```
virtualenv venv
```

In your new virtual environment, clone the repository and cd into the correct repository

```
git clone https://github.com/ucl-team-8/service.git service
cd service
```

Then run these bash commands to set the environment variables in your virtual environment `activate` file:

```
echo "export APP_SETTINGS='config.DevelopmentConfig'" >> venv/bin/activate
echo "export DATABASE_URL='postgres://atos:atos@localhost/atos'" >> venv/bin/activate
```

Activate your virtual environment by running:

```
source venv/bin/activate
```

Finally, install all dependencies from `requirements.txt`:

```
pip install -r requirements.txt
```

### Installing Visualisation Dependencies

To install `node` and `npm` on a Mac, run:

```
brew install node
```

If you don't have brew, see installation instructions [here](http://brew.sh/).

To install `node` and `npm` on Windows, download it from [nodejs.org](https://nodejs.org/en/download/).

After you have `npm`, run:

```
npm install -g jspm
npm install
jspm install
```

Finally, a local environment should be set up.

## Creating the Database Tables

We use `Flask-Migrate` to handle database migrations. To create the necessary database tables, run:

```
python manage.py db upgrade
```

### Importing Data

You will first need to get a copy of the `locations.tsv` file with all of the TIPLOC locations. This file is not publicly available since it is considered confidential information.

To import all of the data in the `data` directory, either run:

```
python import/import.py northern_rail
```

or:

```
python import/import.py east_coast
```

depending on which data set you would like to import.

## Folder Structure

```
.
├── algorithm           # Old iteration of the algorithm
├── algorithm2          # Improved version of the algorithm
├── data                # All of the sample data
|   ├── east_coast      # Extract from the east coast
|      └── ...
|   ├── northern_rail    # Extract from northern rail
|      └── ...
|   ├── locations.tsv   # gitignored file with locations of tiplocs
├── import              # Contains the import script to import data into database.
├── migrations          # All of the database generated by alembic
├── static              # The static files for the client
|   ├── css
|   ├── data            # Can be ignored, is used if you want to directly serve a data file to the client
|   ├── images
|   ├── js          
|      ├── live         # All of the code for the prototype application on client.
|         ├── map       # Uses D3 and leaflet to visualise matching on a map
|         ├── reports   # Renders the reports next to the map
|         ├── services  # Shows all of the services and search
|         ├── utils     # All utility functions
|         └── index.js  # Combines all of the functionality
|   └── ...
├── templates           # All of the html templates that can be rendered
├── tests               # Folder with all of the tests for the python code
├── app_socketio.py     # Deals with clients connecting through socketio
├── app.py              # Serves all of the html web pages
├── config.py           # Flask configurations
├── manage.py           # Manages database models and migrations
├── models.py           # All of the database models
├── package.json        # npm dependencies
├── README.md
├── requirements.txt    # Python packages used
└── ...
```
