import sys
import requests
print("sys.version: "+ sys.version)
print("sys.path: "+ str(sys.path))

class TestRequest:
    def __init__(self, url) -> None:
        self.url = url
        pass
    def get(self) -> str:
        r = requests.get(self.url)
        if(r.status_code == 200):
            return r.text
        return ""
