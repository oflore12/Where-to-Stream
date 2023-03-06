def test1_search_all_query(client):
    getResponse1 = client.get('/')
    # Check that search page could be accessed
    assert getResponse1.status_code == 200

    getResponse2 = client.post('/', data={
        "service": "all",
        "q": "The Simsons",
    })
    # Check that "The Simpsons" was returned as a search result
    assert b"The Simpsons" in getResponse2.data
