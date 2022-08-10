import time
import uuid

import pytest

import simpleinflux

simpleinflux.default_host = "localhost"
simpleinflux.default_port = 8086

db = "test_" + str(uuid.uuid4()).replace("-", "")


@pytest.fixture
def test_db():
    simpleinflux.create_database(db)
    assert db in simpleinflux.get_databases()
    yield
    simpleinflux.drop_database(db)
    assert db not in simpleinflux.get_databases()
