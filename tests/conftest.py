
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Locate backend directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

# Add backend to Python module search path
sys.path.insert(0, str(BACKEND_DIR))

os.environ["SECRET_KEY"] = "pytest-only-secret"

# Import db and prevent database initialization
import db

with patch.object(db, "init_db"):
    import app as app_module


@pytest.fixture
def app():
    app_module.app.config.update(
        TESTING=True,
        SECRET_KEY="pytest-only-secret",
        SESSION_COOKIE_SECURE=False
    )
    yield app_module.app


@pytest.fixture
def client(app):
    return app.test_client()
