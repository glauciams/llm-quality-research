import os
import psycopg2
import json

# In Windows, use the command "setx ENV_VAR_NAME value" or "set ENV_VAR_NAME=value" in the command prompt to set environment variable
# set: Typically used for temporary changes or for scripts that only need the variables for the duration of their execution.
# setx: Used when you need to make persistent changes to environment variables that should be available system-wide or for the current user across all sessions.

# In Linux, use the command "export ENV_VAR_NAME=value" in the terminal to set environment variable

# set DB_NAME=database_name
# set DB_USER=database_user
# set DB_PASSWORD=database_password
# set DB_HOST=database_host_IP

# Database connection parameters
db_params = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': '5432'
}

# Connect to the PostgreSQL database
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Execute the query to fetch data from testdata table

levels = ["introductory", "competition", "interview"]
limit = 10


for level in levels: 
    select_query = f"""
    SELECT problem_id, solutions FROM public.solutions
    WHERE difficulty = '{level}'
    AND solutions IS NOT NULL
    ORDER BY RANDOM() LIMIT {limit}
    """

    cur.execute(select_query)
    
    # Fetch all rows from the executed query
    rows = cur.fetchall()
    
    # Write each solution (array item of each column) to a separate file solution.index_of_array.py
    for row in rows:
        problem_id = row[0]
        print(f"Inserting {problem_id} - {level}")
        solutions = json.loads(row[1])
        for index, solution in enumerate(solutions):
            trimmed_solution = solution.strip()
            
            if trimmed_solution == "":
                continue
            else:
                update_query = """
                INSERT INTO public.formatted_min
                (problem_id,solution)
                VALUES (%s,%s)
                """
                cur.execute(update_query, (problem_id, trimmed_solution))
                break
        
        conn.commit()

cur.close()
conn.close()

print("Solution is updated")
