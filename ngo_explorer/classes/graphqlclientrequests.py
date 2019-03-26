import json

from graphqlclient import GraphQLClient
from flask import current_app
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
        current_app.logger.info("CHARITYBASE {}{}: {}".format(
            "[from cache] " if getattr(r, "from_cache", False) else "",
            self.endpoint,
            json.dumps(variables)
        ))
        r.raise_for_status()
        return r.json()
