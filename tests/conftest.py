# pyrefly: ignore [missing-import]
import pytest
import os
import sqlite3
import utils.database as db

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """
    Redirects utils.database.get_connection to a temporary test database.
    Runs automatically for all tests to ensure data isolation.
    """
    db_file = tmp_path / "test_healthcare.db"
    
    def get_test_connection():
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        return conn
        
    monkeypatch.setattr(db, "get_connection", get_test_connection)
    
    # Initialize the database schema for the test database
    db.init_db()
    
    yield db_file
