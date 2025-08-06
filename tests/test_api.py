import json
import requests


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
