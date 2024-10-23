import os
import requests
import subprocess
import json
import psycopg2
import time
import glob

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

db_params = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': '5432'
}

conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Levels = [introductory, competition, interview]
difficulty = "interview"

# Columns = [solution, solution_cgpt]
column = "solution_cgpt"

result_dump_file = f"results//result_{difficulty}.json"
if column == "solution_cgpt":
    result_dump_file = f"results//result_gpt_{difficulty}.json"


query = f"""
SELECT formatted_min.problem_id, formatted_min.{column}
FROM solutions
INNER JOIN formatted_min ON solutions.problem_id = formatted_min.problem_id
WHERE solutions.difficulty = '{difficulty}'
"""

cur.execute(query)
rows = cur.fetchall()

py_src_dir = "src"

files = glob.glob(f"{py_src_dir}//*.py")
for f in files:
    os.remove(f)

for row in rows:
    problem_id = row[0]
    solution = row[1]
    file_name = f"{py_src_dir}//solution.{problem_id}.py"
    with open(file_name, 'w', encoding="utf-8") as file:
        file.write(solution)

print("Files stored successfully")

sonar_token = os.getenv('SONAR_TOKEN')
project_key = os.getenv('SONAR_PROJECT')
sonar_url = os.getenv('SONAR_SERVER')
src_directory = 'src'
sonar_scanner_path = os.getenv('SONAR_PATH')


# Clean the project on SonarQube server
clean_api_url = f'{sonar_url}/api/projects/delete?project={project_key}'
response = requests.post(clean_api_url, auth=(sonar_token, ''))
if response.status_code == 204:
    print(f'Project {project_key} cleaned successfully.')
else:
    print(f'Failed to clean project {project_key}. Status code: {response.status_code}')
    
time.sleep(5)

# Recreate the project on SonarQube server
create_api_url = f'{sonar_url}/api/projects/create?name={project_key}&project={project_key}'
response = requests.post(create_api_url, auth=(sonar_token, ''))
if response.status_code == 200:
    print(f'Project {project_key} created successfully.')
else:
    print(f'Failed to create project {project_key}. Status code: {response.status_code}')


with open('sonar-project.properties', 'w') as f:
    f.write(f'sonar.projectKey={project_key}\n')
    f.write(f'sonar.sources={py_src_dir}\n')
    f.write(f'sonar.host.url={sonar_url}\n')
    f.write(f'sonar.login={sonar_token}\n')
    f.write(f'sonar.login={sonar_token}\n')
    f.write(f'sonar.scm.disabled=true\n')
    f.write(f'sonar.python.version=3.8\n')

subprocess.run([sonar_scanner_path], check=True)

time.sleep(5)

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

with open(result_dump_file, 'w') as f:
    json.dump(formatted_issues, f, indent=4)

print("Success")
