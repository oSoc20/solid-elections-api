# sep-hackathon-solid
Hackathon project for the Simplification Election Procedures team. This API simply stores a WebID and returns a list of stored WebIDs, which can be used to fetch Solid documents.

## Setup
To install the dependencies needed for this project, you will need [poetry](https://python-poetry.org/) (or manually create a virtual environment). Run `poetry install` to install the required packages. Then to start the server, run `poetry run python src/main.py` in the project root. You can set the `DEBUG` environment variable to start the server in debug mode (verbose logging and auto refresh).


## Warnings
- This project uses a JSON "database", which can result in a race condition that can cause data loss
- The name of a stored WebID is currently controlled by the client. This is probably a bad idea.