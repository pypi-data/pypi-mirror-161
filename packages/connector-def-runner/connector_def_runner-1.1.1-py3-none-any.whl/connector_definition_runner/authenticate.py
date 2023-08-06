
class Authenticate:
    def __init__(self, session, asset, security):
        self.session = session
        self.security = security
        self.asset = asset
        self.params = {}

        self.authentication_handler()

    def authentication_handler(self):
        auth_map = {
            'apiKey': self.apikey_auth,
        }

        auth_map[self.security['type']]()

        return self.session

    def apikey_auth(self):
        switcher = {
            'header': self.session.headers.update({
                self.security['name']: self.asset[self.security['name']]
            }),
            'cookie': NotImplementedError,
            'query': self.params.update({
                self.security['name']: self.asset[self.security['name']]
            }),
        }

        switch = switcher[self.security['in']]

        if callable(switch):
            raise switch()

        return self.session

    def http_auth(self):
        if self.security['scheme'] == 'basic':
            self.session.auth = (self.asset['username'], self.asset['password'])
        elif self.security['scheme'] == 'bearer':
            self.session.headers.update({
                'Authorization': f'Bearer {self.asset["token"]}'
            })
        return self.session

    def oauth2(self):
        switcher = {
            'implicit': NotImplementedError,
            'password': NotImplementedError,
            'clientCredentials': self._client_credentials(),
            'authorizationCode': NotImplementedError
        }

        switch = switcher[self.security['flow']]

        if callable(switch):
            raise switch()

        return self.session

    def _client_credentials(self):
        data = {
            'client_id': self.asset['clientId'],
            'client_secret': self.asset['clientSecret'],
            'scope': self.asset.get('scopes', []).join(' '),
            'grant_type': 'client_credentials'
        }

        token_url = self.asset['tokenUrl']
        access_token = self.session.request("POST", token_url, data=data).json()['access_token']

        self.session.headers.update({"Authorization": "Bearer {}".format(access_token)})
        return self.session
