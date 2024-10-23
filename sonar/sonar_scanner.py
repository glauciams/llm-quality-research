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

# set SONAR_TOKEN=sonarqube api key
# set SONAR_PROJECT=sonarqube api key
# set SONAR_SERVER=sonarqube server ip and port in the format http://<IP>:<PORT>
# set SONAR_PATH=path of sonarqube executable. Example, if Windows, C:\ProgramFiles\Sonar\bin\sonar-scanner.bat

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

sonar_token = os.getenv('SONAR_TOKEN')
project_key = os.getenv('SONAR_PROJECT')
sonar_url = os.getenv('SONAR_SERVER')
src_directory = 'src'
sonar_scanner_path = os.getenv('SONAR_PATH')

with open('sonar-project.properties', 'w') as f:
    f.write(f'sonar.projectKey={project_key}\n')
    f.write(f'sonar.sources={src_directory}\n')
    f.write(f'sonar.host.url={sonar_url}\n')
    f.write(f'sonar.login={sonar_token}\n')

subprocess.run([sonar_scanner_path], check=True)

api_url = f'{sonar_url}/api/issues/search?componentKeys={project_key}'
response = requests.get(api_url, auth=(sonar_token, ''))
issues = response.json()

formatted_issues = []
for issue in issues.get('issues', []):
    formatted_issue = {
        'key': issue['key'],
        'rule': issue['rule'],
        'severity': issue['severity'],
        'file_path': issue['component'].split(':')[1],
        'line': issue.get('line'),
        'message': issue['message'],
        'status': issue['status'],
        'creationDate': issue['creationDate'],
        'updateDate': issue['updateDate'],
        'type': issue['type'],
        'effort': issue['effort'],
        'softwareQuality': issue['impacts'][0]['softwareQuality'] if issue.get('impacts') else None
    }
    formatted_issues.append(formatted_issue)

with open('results//sonar_result.json', 'w') as f:
    json.dump(formatted_issues, f, indent=4)

print("Success")
