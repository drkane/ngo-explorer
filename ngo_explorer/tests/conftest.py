import os

import pytest
import requests_mock

from ngo_explorer import create_app
from ngo_explorer.utils.fetchdata import GQL_QUERIES

thisdir = os.path.dirname(os.path.realpath(__file__))

@pytest.fixture
def client(tmpdir):
    app = create_app({
        'CHARITYBASE_API_KEY': 'test-api-key',
        'TESTING': True,
        'REQUEST_CACHE_BACKEND': 'memory',
        'DATA_CONTAINER': tmpdir.mkdir("upload"),
    })
    client = app.test_client()

    yield client


def graphql_content(request, context):
    q = request.json()
    for g, k in GQL_QUERIES.items():
        if k==q.get("query", ""):
            with open(os.path.join(thisdir, "sample", "charitybase", "{}.json".format(g)), 'rb') as f_:
                return f_.read()
    return False

@pytest.fixture
def m():
    m = requests_mock.Mocker()
    m.register_uri('POST', 'https://charitybase.uk/api/graphql',
                   content=graphql_content)

    with open(os.path.join(thisdir, "sample", "ons", "mm23data.json"), 'rb') as f_:
        m.register_uri('GET', 'https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/l522/mm23/data',
                    content=f_.read())

    m.start()

    return m
