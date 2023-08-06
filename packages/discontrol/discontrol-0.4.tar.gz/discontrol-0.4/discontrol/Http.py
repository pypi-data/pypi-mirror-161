import requests


class DiscordRequest:

    def __init__(self,
                 json: dict,
                 path: str,
                 token: str,
                 type_bot: bool = True,
                 as_user = True):
        self.json = json
        self.token = token
        self.path = path
        if as_user:
          self.headers = {
              "Authorization": f"{'Bot ' if type_bot else ''}{self.token}"
          }
        else:
          self.headers = {}
        self.url = f"https://discord.com/api/v9/{self.path}"

        print(f'[HTTP] Request - {self.url}, {self.headers}, {self.json}')

    def get(self):
        headers = self.headers
        url = self.url
        json = self.json
        response = requests.get(url, headers=headers, json=json)
        return response

    def patch(self):
        headers = self.headers
        url = self.url
        json = self.json
        response = requests.patch(url, headers=headers, json=json)
        return response

    def post(self):
        headers = self.headers
        url = self.url
        json = self.json
        response = requests.post(url, headers=headers, json=json)
        return response

    def put(self):
        headers = self.headers
        url = self.url
        json = self.json
        response = requests.put(url, headers=headers, json=json)
        return response

    def remove(self):
        headers = self.headers
        url = self.url
        json = self.json
        response = requests.remove(url, headers=headers, json=json)
        return response
