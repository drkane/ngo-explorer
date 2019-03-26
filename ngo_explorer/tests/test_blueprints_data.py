

def test_region(client, m):
    rv = client.get('/region/continent/antarctica')
    assert rv.status_code == 200
    assert b'Antarctica' in rv.data
    print(rv.data)
    assert b'4,810' in rv.data
    assert b'10.8bn' in rv.data
    assert b'Dashboard' in rv.data
    assert b'Show NGOs' in rv.data
    assert b'Download' in rv.data
    assert b'IATI Activity data' in rv.data
    assert b'Other resources' in rv.data
    assert b'How NGOs describe themselves' in rv.data
    assert b'id="min-income"' in rv.data
    assert b'https://devtracker.dfid.gov.uk/countries/AQ/' in rv.data
    assert b'<span id="charity-count">4,810 UK NGOs</span>' in rv.data

    rv = client.get('/region/undp/arab-states')
    assert rv.status_code == 200
    assert b'United Nations Development Programme region' in rv.data

    rv = client.get('/region/dac/lower-middle-income')
    assert rv.status_code == 200
    assert b'OECD Development Assistance Committee group' in rv.data


def test_region_list(client, m):
    rv = client.get('/region/continent/antarctica/show-charities')
    assert rv.status_code == 200
    assert b'Antarctica' in rv.data
    assert b'4,810' in rv.data
    assert b'Dashboard' in rv.data
    assert b'Show NGOs' in rv.data
    assert b'Download' in rv.data
    assert b'Next' in rv.data
    assert b'The Children\'s Investment Fund Foundation (UK)' in rv.data
    assert b'Latest income' in rv.data

    rv = client.get(
        '/region/continent/europe/show-charities?filter-skip=30')
    assert rv.status_code == 200
    assert b'Europe' in rv.data
    assert b'4,810' in rv.data
    assert b'Dashboard' in rv.data
    assert b'31' in rv.data
    assert b'60' in rv.data


def test_region_download(client, m):
    rv = client.get('/region/continent/antarctica/download')
    assert rv.status_code == 200
    assert b'Antarctica' in rv.data
    assert b'4,810' in rv.data
    assert b'Dashboard' in rv.data
    assert b'Show NGOs' in rv.data
    assert b'Download' in rv.data
    assert b'Downloads are limited to 500 records' in rv.data
    assert b'Latest income' in rv.data


def test_region_json(client, m):
    rv = client.get('/region/continent/antarctica.json')
    assert rv.status_code == 200
    data = rv.get_json()
    for i in ['area', 'charts', 'filters', 'inserts', 'pages']:
        assert i in data.keys()
    assert b'Antarctica' in rv.data
    assert b'4,810' in rv.data


def test_region_list_json(client, m):
    rv = client.get('/region/continent/antarctica/show-charities.json')
    assert rv.status_code == 200
    data = rv.get_json()
    for i in ['area', 'charts', 'filters', 'inserts', 'pages']:
        assert i in data.keys()
    assert b'Antarctica' in rv.data
    assert b'4,810' in rv.data
    assert b'Dashboard' in rv.data
    assert b'Show NGOs' in rv.data
    assert b'Download' in rv.data
    assert b'Next' in rv.data
    assert b'The Children\'s Investment Fund Foundation (UK)' in rv.data
    assert b'Latest income' in rv.data


def test_region_missing(client, m):
    rv = client.get('/region/continent/blooblar')
    assert rv.status_code == 404


def test_country(client, m):
    rv = client.get('/country/ben')
    assert rv.status_code == 200
    assert b'Benin' in rv.data
    assert b'4,810' in rv.data
    assert b'10.8bn' in rv.data
    assert b'Dashboard' in rv.data
    assert b'Show NGOs' in rv.data
    assert b'Download' in rv.data
    assert b'IATI Activity data' in rv.data
    assert b'Other resources' in rv.data
    assert b'How NGOs describe themselves' in rv.data
    assert b'id="min-income"' in rv.data
    assert b'https://ngoaidmap.org/location/gn_2395170' in rv.data
    assert b'https://devtracker.dfid.gov.uk/countries/BJ/' in rv.data
    assert b'http://www.cfrong.org/' in rv.data
    assert b'<span id="charity-count">4,810 UK NGOs</span>' in rv.data


def test_country_list(client, m):
    rv = client.get('/country/ben/show-charities')
    assert rv.status_code == 200
    assert b'Benin' in rv.data
    assert b'4,810' in rv.data
    assert b'Dashboard' in rv.data
    assert b'Show NGOs' in rv.data
    assert b'Download' in rv.data
    assert b'Next' in rv.data
    assert b'The Children\'s Investment Fund Foundation (UK)' in rv.data
    assert b'Latest income' in rv.data

    rv = client.get(
        '/country/ben/show-charities?filter-skip=30')
    assert rv.status_code == 200
    assert b'Benin' in rv.data
    assert b'4,810' in rv.data
    assert b'Dashboard' in rv.data
    assert b'31' in rv.data
    assert b'60' in rv.data


def test_country_download(client, m):
    rv = client.get('/country/ben/download')
    assert rv.status_code == 200
    assert b'Benin' in rv.data
    assert b'4,810' in rv.data
    assert b'Dashboard' in rv.data
    assert b'Show NGOs' in rv.data
    assert b'Download' in rv.data
    assert b'Downloads are limited to 500 records' in rv.data
    assert b'Latest income' in rv.data


def test_country_json(client, m):
    rv = client.get('/country/ben.json')
    assert rv.status_code == 200
    data = rv.get_json()
    for i in ['area', 'charts', 'filters', 'inserts', 'pages']:
        assert i in data.keys()
    assert b'Benin' in rv.data
    assert b'4,810' in rv.data


def test_country_list_json(client, m):
    rv = client.get('/country/ben/show-charities.json')
    assert rv.status_code == 200
    data = rv.get_json()
    for i in ['area', 'charts', 'filters', 'inserts', 'pages']:
        assert i in data.keys()
    assert b'Benin' in rv.data
    assert b'4,810' in rv.data
    assert b'Dashboard' in rv.data
    assert b'Show NGOs' in rv.data
    assert b'Download' in rv.data
    assert b'Next' in rv.data
    assert b'The Children\'s Investment Fund Foundation (UK)' in rv.data
    assert b'Latest income' in rv.data


def test_country_missing(client, m):
    rv = client.get('/country/blooblar')
    assert rv.status_code == 404
