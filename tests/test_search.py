def test1_search_all_query(client):
    getResponse = client.get('/results', query_string={
        "service": "all",
        "q": "The Simpsons",
    })
    # Check that "The Simpsons" was returned as a search result
    assert b"The Simpsons" in getResponse.data
