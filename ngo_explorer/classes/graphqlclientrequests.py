from graphqlclient import GraphQLClient
import requests

class GraphQLClientRequests(GraphQLClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _send(self, query, variables):
        data = {'query': query,
                'variables': variables}
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

        if self.token is not None:
            headers[self.headername] = '{}'.format(self.token)

        r = requests.post(self.endpoint, json=data, headers=headers)
        r.raise_for_status()
        return r.json()
