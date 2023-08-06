import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path

class Intaqt:
    url = "https://api.intaqt.cloud/api/v1/"

    def __init__(self, key=""):
        print(self.url)
        self.api_key    = key
        self.headers    = {
            'Authorization': f'Token {self.api_key}'
            }

    def send(self, content, status):
        data = {
            "status"    : status,
            "data"      : content,
        }
        url = self.url + f"data/notifications"
        try:
            r = requests.post(
                url,
                headers=self.headers,
                data = data
            )
        except:
            print('Request not succesful')
            return False
        else:
            print(r.text)
            print(f'Request with status code {r.status_code}')
        return True
