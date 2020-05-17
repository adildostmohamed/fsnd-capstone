# fsnd-capstone

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

#### Start Local Development
##### Database Setup
- Set up a dev database and add it to your `.env` file as `DEV_DB` or replace the db name directly (currently named `casting_dev`)
- With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:

```bash
psql casting_dev < test_db.psql
```
##### Run backend
- run `python3 app.py` which will start the backend with debug mode on on port `localhost:8080`
#### Testing
##### Run tests
- Set up a test database and add it to your `.env` file as `TEST_DB` or replace the db name directly (currently named `casting_test`)

```
dropdb casting_test
createdb casting_test
psql casting_test < test_db.psql
python test_app.py
```
