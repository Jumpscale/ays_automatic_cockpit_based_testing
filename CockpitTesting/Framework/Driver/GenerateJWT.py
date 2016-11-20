import requests
import json

params = {
        'grant_type': 'client_credentials',
        'client_id': 'quality_cockpit_',
        'client_secret': 'ymVtPAgrm8AQB7cpdpY0d7yBFE1YtUFc_Z84F0uESzg7ErxiPWK_'
}

url = 'https://itsyou.online/v1/oauth/access_token?'
resp = requests.post(url, params=params,verify=False)
resp.raise_for_status()
access_token = resp.json()['access_token']
url = 'https://itsyou.online/v1/oauth/jwt'
headers = {'Authorization': 'token %s' % access_token}
data = {'scope': 'user:memberOf:%s' % 'quality_cockpit_'}
resp = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
print(resp.content)
