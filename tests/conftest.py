import os

os.environ.setdefault("DB_PASSWORD", "test-only")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Asset


@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db:
        db.add(Asset(asset_tag="SRV-TEST", name="Test Server", asset_type="Server", owner="Test Team", environment="Test", status="Active", location="Test Lab", operating_system="Linux"))
        db.commit()
        yield db


@pytest.fixture
def client(session, monkeypatch):
    app.dependency_overrides[get_db] = lambda: session
    monkeypatch.setattr("app.main.check_database", lambda: True)
    monkeypatch.setattr("app.main.initialize_database", lambda: None)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
