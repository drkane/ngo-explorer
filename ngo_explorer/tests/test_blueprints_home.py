def test_index_page(client):
    rv = client.get('/')
    assert b'Explore UK charities working across the world' in rv.data
    assert b'Type to search' in rv.data
    assert b'Europe and Central Asia' in rv.data
    assert b'Upper middle income' in rv.data
    assert b'Upload your data' in rv.data
    assert b'CharityBase' in rv.data
    assert b'GCRF Global Impact Accelerator' in rv.data

def test_about_page(client):
    rv = client.get('/about')
    assert b'Sheffield Institute for International Development' in rv.data
    assert b'Global Development Institute' in rv.data
    assert b'David Kane' in rv.data
    assert b'CharityBase' in rv.data
    assert b'UK Research and Innovation' in rv.data
    assert b'GCRF Global Impact Accelerator' in rv.data
