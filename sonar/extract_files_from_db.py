import os
import requests
import subprocess
import json
import psycopg2

# In Windows, use the command "setx ENV_VAR_NAME value" or "set ENV_VAR_NAME=value" in the command prompt to set environment variable
# set: Typically used for temporary changes or for scripts that only need the variables for the duration of their execution.
# setx: Used when you need to make persistent changes to environment variables that should be available system-wide or for the current user across all sessions.

# In Linux, use the command "export ENV_VAR_NAME=value" in the terminal to set environment variable

# set DB_NAME=database_name
# set DB_USER=database_user
# set DB_PASSWORD=database_password
# set DB_HOST=database_host_IP

db_params = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': '5432'
}

conn = psycopg2.connect(**db_params)
cur = conn.cursor()

query = """
SELECT problem_id, solution, solution_cgpt
FROM public.formatted_min
"""

cur.execute(query)
rows = cur.fetchall()

for row in rows:
    problem_id = row[0]
    human_solution = row[1]
    cgpt_solution = row[2]
    human_file_name = f"src//solution_human.{problem_id}.py"
    with open(human_file_name, 'w', encoding="utf-8") as file:
        file.write(human_solution)
    cgpt_file_name = f"src//solution_cgpt.{problem_id}.py"
    with open(cgpt_file_name, 'w', encoding="utf-8") as file:
        file.write(cgpt_solution)

print("Files stored successfully")
