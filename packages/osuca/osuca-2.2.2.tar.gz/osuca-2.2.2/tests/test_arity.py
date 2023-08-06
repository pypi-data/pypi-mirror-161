import pytest
from osuca.db import get_db


def test_legend(client):
    response = client.get('/arity/')
    assert b"Number of Evaluations" in response.data
    assert b"Average Course Difficulty" in response.data

def test_data(client):
    response = client.get('/arity/')
    assert b"'sum': 650" in response.data

def test_status(client):
    assert client.get('/arity/').status_code == 200
