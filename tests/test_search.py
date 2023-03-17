import pytest


@pytest.mark.parametrize(
    'name',
    [
        'The Simpsons',
        'The Bourne Ultimatum',
        'The Dark Knight',
        'Breaking Bad'
    ],
)
def test1_search_all_b(client, name):
    getResponse = client.get('/results', query_string={
        'service': 'all',
        'q': name,
    })
    # Check that query was returned as a search result
    assert bytes(name, encoding='utf-8') in getResponse.data


def test2_search_all_w(client):
    pass


def test3_search_filter_b(client):
    pass


def test4_search_filter_w(client):
    pass
