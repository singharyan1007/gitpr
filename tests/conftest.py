import os

import pytest

# Point at a throwaway sqlite file so tests never touch dev data.
os.environ.setdefault("GITHUB_TOKEN", "test-token")
os.environ.setdefault("WEBHOOK_SECRET", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_reviews.db")


@pytest.fixture(autouse=True, scope="session")
def _cleanup_test_db():
    yield
    if os.path.exists("test_reviews.db"):
        os.remove("test_reviews.db")
