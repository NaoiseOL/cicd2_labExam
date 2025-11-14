import pytest
from fastapi.testclient import testclient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models import Base, CustomerDB, OrderDb

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_create_customer_ok(client):
    r = client.post("/api/customers", json = (name = "naoise", email= ))