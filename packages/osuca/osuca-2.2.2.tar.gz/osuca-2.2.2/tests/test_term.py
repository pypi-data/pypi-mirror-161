import pytest
from osuca.db import get_db


def test_legend(client):
    response = client.get('/')
    assert b"Number of Evaluations" in response.data
    assert b"Average Course Difficulty" in response.data

def test_data(client):
    response = client.get('/')
    assert b"'mean': 2.6937799043062203" in response.data

def test_status(client):
    assert client.get('/').status_code == 200

def test_redirect(client):
    assert client.get('/term').status_code == 308 