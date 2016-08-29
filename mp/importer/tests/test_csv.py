import pytest

"""Test the import_from_csv library
"""

def make_factory(mp_pg_service):
    from ..sql import get_versions
    from ..fixtures import DatabaseFactory
    return DatabaseFactory(
            mp_pg_service,
            get_versions(allow_latest=True)[-1],
            db_type='empty',
            db_locale='en',
            allow_latest=True)

@pytest.fixture(scope='session')
def source_database_factory(mp_pg_service):
    return make_factory(mp_pg_service)

@pytest.fixture(scope='session')
def target_database_factory(mp_pg_service):
    return make_factory(mp_pg_service)

def make_db(request, database_factory):
    from mp.db.fixtures import Database
    db = Database(database_factory)
    db.setup()
    def finalizer():
        db.cleanup()
    request.addfinalizer(finalizer)
    return db

@pytest.fixture
def target_db(request, target_database_factory):
    return make_db(request, target_database_factory)

@pytest.fixture
def source_db(request, source_database_factory):
    return make_db(request, source_database_factory)

def connect(request, db):
    from psycopg2 import connect
    conn = connect(host=db.host, port=db.port, database=db.database)
    def close():
        conn.rollback()
        conn.close()
    request.addfinalizer(close)
    return conn

@pytest.fixture
def source(request, source_db):
    return connect(request, source_db)

@pytest.fixture
def target(request, target_db):
    return connect(request, target_db)



# define what we expect from this library and write tests
# not sure if I need all the fixtures for the connection

# test also the geonames part...

# test put location
def test_simple():
    from ..mp.importer import csv
    # assert something







