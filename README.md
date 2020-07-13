# sep-hackathon-solid
Hackathon project for the Simplification Election Procedures team. This API simply stores a WebID and returns a list of stored WebIDs, which can be used to fetch Solid documents.


## Setup
To install the dependencies needed for this project, you will need [poetry](https://python-poetry.org/) (or manually create a virtual environment). Run `poetry install` to install the required packages. Then to start the server, run `poetry run python src/main.py` in the project root. You can set the `DEBUG` environment variable to start the server in debug mode (verbose logging and auto refresh).

For the database, you will need a PostgreSQL instance. This can be done by setting up a [postgress Docker image](https://hub.docker.com/_/postgres) (don't forget to forward port `5432`) or setting it up regularly. You will also need to create a `secret.py` file in the `src/` folder that sets the following varibales: `PG_HOST`, `PG_DBNAME`, `PG_USER` and `PG_PASS`. For the Docker postgres image, the default DBNAME and USER are `postgres`.


## Warnings
- The name of a stored WebID is currently controlled by the client. This is probably a bad idea.