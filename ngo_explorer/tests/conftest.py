import os

import pytest
import requests_mock

from ngo_explorer import create_app

thisdir = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def client(tmpdir):
    app = create_app(
        {
            "TESTING": True,
            "REQUEST_CACHE_BACKEND": "memory",
            "DATA_CONTAINER": tmpdir.mkdir("upload"),
            "DB_LOCATION": os.path.join(thisdir, "sample", "charitydata.sqlite"),
        }
    )
    client = app.test_client()

    yield client


@pytest.fixture
def m():
    m = requests_mock.Mocker()

    with open(os.path.join(thisdir, "sample", "ons", "mm23data.json"), "rb") as f_:
        m.register_uri(
            "GET",
            "https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/l522/mm23/data",
            content=f_.read(),
        )

    m.start()

    return m
