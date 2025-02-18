Documentation For Project Zero Proof

sections:

- Dev Environment Setup

  1. **Install Docker:**
  2. **Create a Docker network named `fastapi_template_project_network` if not exists:**
     ```
     docker network create fastapi_template_project_network
     ```
  3. **Run Docker Compose:**
     In each repository directory, run the following commands:

     ```bash
     cd fastapi-starter-template
     cp .env.example .env
     docker compose build # build the project
     docker compose up -d # run project in detached mode
     docker compose exec fastapi-starter-template migrate # run migrations
     ```

  4. **Access Services:**
     When you have done this you will have docker containers running for all services required. You can then connect to localhost with the following ports for each service:

     - Fast API Template Projct: [http://localhost:16000](http://localhost:16000)

  5. **Auto-Deploy Changes:**
     Any changes made using the IDE (PyCharm) will be reflected in the services as they auto-reload.

- Debug Environment Setup

  1. **Run Docker Compose:**
     In each repository directory there are docker compose debug file, these compose file run the fast api in debug mode using python debugpy library.

     Run the following commands to run them:

     ```bash
     cd fastapi-starter-template
     docker-compose -f docker-compose.debug.yml build
     docker-compose -f docker-compose.debug.yml up -d
     ```

     currently all the service interacts with debugpy at 5678 port may be it needs to be changed when you want to up and debug all services at once.

  2. **Setup Remote Debug in Visual Studio Code**
     1. Create a remote debug configuration file at .vscode/launch.json
        Configuration Sample
     ```
     {
          // Use IntelliSense to learn about possible attributes.
          // Hover to view descriptions of existing attributes.
          // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
          "version": "0.2.0",
          "configurations": [
              {
                  "name": "Python: Remote Attach",
                  "type": "python",
                  "request": "attach",
                  "connect": {
                      "host": "localhost",
                      "port": 5678
                  },
                  "pathMappings": [
                      {
                          "localRoot": "${workspaceFolder}/fastapi-starter-template", # the root project folder path
                          "remoteRoot": "."
                      }
                  ],
                  "justMyCode": true
              }
          ]
      }
     ```
     2. Go to Run and Debug tab
     3. Click on `Python:  Remote Attach Branch` a Green button and you are good to go for debug mode.
  3. **Access Services:**
     When you have done this you will have docker containers running for all services required. You can then connect to localhost with the following ports for each service:
     - Fastapi Template Project: [http://localhost:16000](http://localhost:16000)

- Requirements

  - If you need to add requirements the requirements are hosted in the {PROJET}/requirements folder
  - There are three files:
    - Base.txt: All requirements across environments.
    - Dev.txt: Requirements needed for the development environment.
    - Prod.txt: Requirements needed for the production environment.

- Code Structure

  - Code structure based on [FastAPI Production Template](https://github.com/zhanymkanov/fastapi_production_template).
  - At a high level here are some key pieces of information:
  - All code is located in the src directory
  - `src` directory contains:

    - `config.py`: Configuration items.
    - `constants.py`: Global constants.
    - `database.py`: Database setup (using SQLAlchemy and Alembic).
    - `exceptions.py`: Custom exceptions.
    - `main.py`: Main entry point. Key here is as we add additional subdirectories you need to add a router reference
    - `models.py`: Uses Pydantic for object serialization etc. Custom base model `ZPModel` has been created and any object we want to serialize should inherit from this class. Right now it has customizations that convert datetime’s to GMT. More can be done with this long term.
    - `redis.py`: We don’t leverage redis yet but this code will allow us to add and get information from redis using pydantic

    - `utils.py`: Any global functions we might want to build. Note: currently there is nothing in this file of use.

  - In addition to the common src files we create a directory for each top level path router. In this directory we create the following files to contain that path’s logic. Inside this directory it may have the following files:

    - `config.py`: Configuration items.
    - `constants.py`: Any Local constants.
    - `dependencies.py`: Any Validation logic.
    - `exceptions.py`: Any exceptions local to the path to be thrown
    - `router.py`: contains router handlers for each possible call to the directory

    - `schemas.py`: class definitions for objects that we will serialize and serialize to json, sql, etc

    - `security.py`: Any Security level functions.
    - `service.py`: This is the meat of the code and contains the business logic
    - `utils.py`: Any local functions we might want to build.

  - As needed we can add additional structure but this convention works pretty well and is easy to navigate

- Repository Structure

  - [fastapi-starter-template](URL/fastapi-starter-template): Description.

- some configs for production
  - gunicorn with dynamic workers configuration (stolen from [@tiangolo](https://github.com/tiangolo))
  - Dockerfile optimized for small size and fast builds with a non-root user
  - JSON logs
  - sentry for deployed envs
- easy local development
  - environment with configured postgres and redis
  - script to lint code with `ruff` and `ruff format`
  - configured pytest with `async-asgi-testclient`, `pytest-env`, `pytest-asyncio`
- SQLAlchemy with slightly configured `alembic`
  - async SQLAlchemy engine
  - migrations set in easy to sort format (`YYYY-MM-DD_slug`)
- pre-installed JWT authorization
  - short-lived access token
  - long-lived refresh token which is stored in http-only cookies
  - salted password storage with `bcrypt`
- global pydantic model with
  - explicit timezone setting during JSON export
- and some other extras like global exceptions, sqlalchemy keys naming convention, shortcut scripts for alembic, etc.

Current version of the template (with SQLAlchemy >2.0 & Pydantic >2.0) wasn't battle tested on production,
so there might be some workarounds instead of neat solutions, but overall idea of the project structure is still the same.

### Linters

Format the code with `ruff --fix` and `ruff format`

```shell
docker compose exec fastapi-starter-template format
```

### Migrations

- Create an automatic migration from changes in `src/database.py`

```shell
docker compose exec fastapi-starter-template makemigrations *migration_name*
```

- Run migrations

```shell
docker compose exec fastapi-starter-template migrate
```

- Downgrade migrations

```shell
docker compose exec fastapi-starter-template downgrade -1  # or -2 or base or hash of the migration
```

### Tests

All tests are integrational and require DB connection.

- Tests are run with upgrading & downgrading alembic migrations. It's not perfect, but works fine.

Run tests

```shell
docker compose exec fastapi-starter-template pytest
```

### Justfile

The template is using [Just](https://github.com/casey/just).

It's a Makefile alternative written in Rust with a nice syntax.

You can find all the shortcuts in `justfile` or run the following command to list them all:

```shell
just --list
```

Info about installation can be found [here](https://github.com/casey/just#packages).

### Backup and Restore database

We are using `pg_dump` and `pg_restore` to backup and restore the database.

- Backup

```shell
just backup
# output example
Backup process started.
Backup has been created and saved to /backups/backup-year-month-date-HHMMSS.dump.gz
```

- Copy the backup file or a directory with all backups to your local machine

```shell
just mount-docker-backup  # get all backups
just mount-docker-backup backup-year-month-date-HHMMSS.dump.gz  # get a specific backup
```

- Restore

```shell
just restore backup-year-month-date-HHMMSS.dump.gz
# output example
Dropping the database...
Creating a new database...
Applying the backup to the new database...
Backup applied successfully.
```
