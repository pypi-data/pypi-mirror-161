import pytest
from osuca.db import get_db


def test_data(client):
    response = client.get('/combination/count/True')
    assert b"<td>3.09</td>" in response.data

def test_status(client):
    assert client.get('/combination/count/True').status_code == 200
