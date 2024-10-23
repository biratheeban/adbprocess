import os
import requests

######################
# Jenkins
jenkins_url = 'http://jenkins_url_here'
username = 'your_username'  
password = 'your_password'  
######################


session = requests.Session()

# Login URL
login_url = f'{jenkins_url}/j_acegi_security_check'

# Send authentication request with username and password
try:
    auth_response = session.post(login_url, auth=(username, password))
    print(f'Status Code: {auth_response.status_code}')
    print(f'Response Content: {auth_response.text}')
except requests.exceptions.RequestException as e:
    print(f'Error during request: {e}')
