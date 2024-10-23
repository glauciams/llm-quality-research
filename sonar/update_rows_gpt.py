import os
import requests
import psycopg2
import json
import re
import time

def call_chatgpt(prompt_text):
    data = {
        'model': 'gpt-4o',
        'messages': [{'role': 'user', 'content': prompt_text}],
        'temperature': 0.2
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def extract_code(content):
    code_blocks = re.findall(r'```python(.*?)```', content, re.DOTALL)
    return '\n'.join(code_blocks).strip()

# In Windows, use the command "setx ENV_VAR_NAME value" or "set ENV_VAR_NAME=value" in the command prompt to set environment variable
# set: Typically used for temporary changes or for scripts that only need the variables for the duration of their execution.
# setx: Used when you need to make persistent changes to environment variables that should be available system-wide or for the current user across all sessions.

# In Linux, use the command "export ENV_VAR_NAME=value" in the terminal to set environment variable

# set CGPT_API_KEY=ChatGPT API Token

# set DB_NAME=database_name
# set DB_USER=database_user
# set DB_PASSWORD=database_password
# set DB_HOST=database_host_IP

api_key = os.getenv('CGPT_API_KEY')

url = 'https://api.openai.com/v1/chat/completions'

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

prompt = "Generate a Python code (only one solution) to solve this question - \n"

# Database connection parameters
db_params = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': '5432'
}

conn = psycopg2.connect(**db_params)
cur = conn.cursor()

join_query = """
SELECT formatted_min.problem_id, solutions.question
FROM public.formatted_min JOIN public.solutions
ON formatted_min.problem_id = solutions.problem_id
"""

cur.execute(join_query)

rows = cur.fetchall()

for row in rows:
    problem_id = row[0]
    question = row[1]
    
    print(f"Processing problem ID {problem_id}")
    
    gpt_start_time = time.time()

    response_json = call_chatgpt(prompt + question)
    content = response_json['choices'][0]['message']['content']
    code = extract_code(content)
    
    if code == "":
        print(f"Code is empty. Problem id {problem_id}")
        
        dump_file_name = f"dump//chatgpt_response.{problem_id}.json"
        with open(dump_file_name, 'w', encoding="utf-8") as chatgpt_dump_file:
            json.dump(response_json, chatgpt_dump_file)
        
        content_file_name = f"dump//chatgpt_response.{problem_id}.txt"
        with open(content_file_name, 'w', encoding="utf-8") as content_file:
            content_file.write(content)
    else:
        gpt_end_time = time.time()
        sql_start_time = time.time()
        
        update_query = """
        UPDATE public.formatted_min
        SET solution_cgpt = %s
        WHERE problem_id = %s
        """
        cur.execute(update_query, (code, problem_id))
        conn.commit()
        
        sql_end_time = time.time()
        
        gpt_duration = int(gpt_end_time - gpt_start_time)
        sql_duration = int(sql_end_time - sql_start_time)
        
        print(f"Problem ID {problem_id} processed successfully.. Took {gpt_duration} seconds for ChatGPT and {sql_duration} seconds for SQL")

cur.close()
conn.close()

print("ChatGPT solutions are updated")