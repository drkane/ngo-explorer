def test_index_page(client):
    rv = client.get('/upload/')
    assert b'Upload your own data' in rv.data
    assert b'https://findthatcharity.uk/adddata' in rv.data
    assert b'Fetch data on these charities' in rv.data
    assert b'Paste a list of charity numbers' in rv.data

def test_upload_process(client, m):
    rv = client.post(
        '/upload/', data={"charitynumbers": "225922,301020,1001337"})
    assert rv.status_code == 303
    rv = client.get(rv.headers["Location"])
    assert b'Data on 4,810 charities' in rv.data
    
    rv = client.post(
        '/upload/', data={"upload-name": "Test Upload 1234", "charitynumbers": "225922,301020,1001337"})
    upload_url = rv.headers["Location"]
    assert rv.status_code == 303

    rv = client.get(upload_url)
    assert b'Test Upload 1234' in rv.data
    assert b'Data on 4,810 charities' in rv.data

    rv = client.get(upload_url + '/show-charities')
    assert b'Test Upload 1234' in rv.data
    assert b'Data on 4,810 charities' in rv.data
    
    rv = client.get(upload_url + '/download')
    assert b'Test Upload 1234' in rv.data
    assert b'Data on 4,810 charities' in rv.data
    assert b'Latest income' in rv.data
    
