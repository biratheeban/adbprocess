import requests

# Jenkins 
jenkins_url = 'https://your-jenkins-url.com'
username = 'username'
api_token = 'api_token'

api_url = f'{jenkins_url}/api/json'

# Send 
try:
    response = requests.get(api_url, auth=(username, api_token))
    
    if response.status_code == 200:
        print('Login successful!')
        print(response.json())
    else:
        print(f'Failed to log in. Status Code: {response.status_code}')
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f'Error during request: {e}')
