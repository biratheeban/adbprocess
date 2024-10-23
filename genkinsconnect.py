
import requests

######################
# Jenkins
jenkins_url = 'ip or url of jenkins'
username = 'username'
api_token = 'api-token'
######################

# Startsession
session = requests.Session()

#URL
login_url = f'{jenkins_url}/j_acegi_security_check'

# Send authentication request
try:
    auth_response = session.post(login_url, auth=(username, api_token))
    print(f'Status Code: {auth_response.status_code}')
    print(f'Response Content: {auth_response.text}')
except requests.exceptions.RequestException as e:
    print(f'Error during request: {e}')
