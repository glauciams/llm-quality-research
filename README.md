# Setting up Environment

We are creating applications based on LLMs.

Before we begin, let's make sure you have your environment set up.

## Tools

We will use Python as the programming language and Postgres as the database. Make sure you have installed and configured both. Recommended versions:

- Python: 3.10 or higher
- PostgreSQL: 15 or higher

All other dependencies will be installed via `pip`.

## Create a Virtual Environment and Install Python Dependencies

To avoid conflicts between your system libraries, it's recommended to create a separate virtual environment.

```
python3 -m venv env
source env/bin/activate
```

Next, install the libraries:

```
pip install -r requirements.txt
```

## Install the pgvector Extension for Postgres

PGVector is a very important tool for creating LLM-based applications, as it provides new types of data storage and retrieval. To install it, follow the instructions below.

For Linux users, pgvector can be installed via APT:

```
sudo apt install postgresql-16-pgvector
```

For macOS users, you can use homebrew:

```
brew install pgvector
```

For other installation methods, refer to the [official repository](https://github.com/pgvector/pgvector).

### Create a Database in Postgres

Once installed, create a database and a table using the `VECTOR` type. First, connect via command line to your database;

```bash
$ psql -h 127.0.0.1 -U postgres
```

Once connected, run the script below to create the database and table.

```sql 
CREATE DATABASE bootcamp_llm;

\c bootcamp_llm

CREATE EXTENSION IF NOT EXISTS vector;

DROP TABLE IF EXISTS embeddings;

CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT,
    chars INTEGER,
    embeddings VECTOR
);
```

## Configure Access to OpenAI

Much of our work will be based on OpenAI APIs. To do this, you need to create a key to access the [OpenAI platform](https://platform.openai.com/). 

Then, add the environment variable `OPENAI_API_KEY` to the `.env` file.

```
OPENAI_API_KEY = "<KEY>"
```

## Run the Web Interface

Finally, to ensure that the configuration was successful, run the following command:

- `python3 file.py`

## Dataset in use for first release:

https://www.kaggle.com/datasets/thedevastator/coding-questions-with-solutions
