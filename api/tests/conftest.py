from contextlib import contextmanager
from datetime import datetime

import factory
import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from testcontainers.postgres import PostgresContainer

from app.app import app
from app.core.database import get_session
from app.models.base import table_registry
from app.core.settings import Settings


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:17', driver='psycopg') as postgres:
        yield create_engine(postgres.get_connection_url())


@pytest.fixture
def session(engine):

    table_registry.metadata.create_all(engine)

    with Session(engine, expire_on_commit=False) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def settings():
    return Settings()
