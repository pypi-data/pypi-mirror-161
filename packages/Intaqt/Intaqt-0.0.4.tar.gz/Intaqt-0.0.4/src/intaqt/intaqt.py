import requests
from requests.auth import HTTPBasicAuth
from .settings import API_URL

class Intaqt:
    url = API_URL

    def __init__(self, key=""):
        print(f'Intaqt: api key {key}')
        self.api_key    = key
        self.headers    = {
            'Authorization': f'Token {self.api_key}'
            }
        #self.auth       = HTTPBasicAuth('apikey', self.api_key)

    def send(self, id, status, content):
        print('Sending data ...')
        data = {
            "data" : content,
        }
        url = self.url+f"{id}/notifications/{status}"
        try:
            r = requests.post(
                url,
                headers=self.headers,
                data = data
            )#, auth=self.auth)
        except:
            print('Request not succesful')
            return False
        else:
            print(r.text)
            print(f'Request with status code {r.status_code}')
        return True

#i = Intaqt('0542347cd5cb7c8fac45dc4f832c889cb93a083c')
#i.send(1, 'error', 'ein anderer test fuer project 2')
