import os
import sys
import time
from pathlib import Path

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

BASE = os.getenv("TEST_API_URL", "http://127.0.0.1:8000")


@pytest.fixture(scope="session", autouse=True)
def wait_for_api():
    for _ in range(60):
        try:
            r = requests.get(f"{BASE}/api/health", timeout=2)
            if r.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    pytest.fail("API not available at " + BASE)


@pytest.fixture
def api():
    return BASE


@pytest.fixture
def unique_email():
    import uuid
    return f"pig_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def db_session():
    from app.db.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()