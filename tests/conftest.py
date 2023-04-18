import pytest
from ..app import app


@pytest.fixture
def client():
    app.testing = True
    client = app.test_client()
    yield client
