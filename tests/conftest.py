"""Integration tests against a real MySQL server.

They use a dedicated database (MYSQL_TEST_DB, default ``flaskcrud_test``)
which is dropped and recreated, so they never touch your real data.
Connection settings come from the usual MYSQL_* environment variables.
"""
import os
import sys

import MySQLdb
import pytest

APP_DIR = os.path.join(os.path.dirname(__file__), "..", "app")
sys.path.insert(0, os.path.abspath(APP_DIR))

TEST_DB = os.getenv("MYSQL_TEST_DB", "flaskcrud_test")
os.environ["MYSQL_DB"] = TEST_DB

SCHEMA = """
CREATE TABLE contacts(
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  fullname VARCHAR(255),
  phone VARCHAR(255),
  email VARCHAR(255) NOT NULL UNIQUE
)
"""


def _server_conn():
    return MySQLdb.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        port=int(os.getenv("MYSQL_PORT", 3306)),
    )


@pytest.fixture(scope="session")
def flask_app():
    try:
        conn = _server_conn()
    except MySQLdb.OperationalError as exc:
        pytest.skip(f"MySQL not available: {exc}")
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS `{TEST_DB}`")
    cur.execute(f"CREATE DATABASE `{TEST_DB}`")
    cur.execute(f"USE `{TEST_DB}`")
    cur.execute(SCHEMA)
    conn.commit()
    conn.close()
    from main import app  # noqa: E402  (needs sys.path + env set above)

    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    yield app

    conn = _server_conn()
    conn.cursor().execute(f"DROP DATABASE IF EXISTS `{TEST_DB}`")
    conn.close()


@pytest.fixture(autouse=True)
def fresh_db(flask_app):
    conn = _server_conn()
    conn.cursor().execute(f"DELETE FROM `{TEST_DB}`.contacts")
    conn.commit()
    conn.close()


@pytest.fixture
def client(flask_app):
    return flask_app.test_client()


@pytest.fixture
def db_rows():
    def fetch():
        conn = _server_conn()
        cur = conn.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(f"SELECT * FROM `{TEST_DB}`.contacts ORDER BY id")
        rows = cur.fetchall()
        conn.close()
        return list(rows)

    return fetch
