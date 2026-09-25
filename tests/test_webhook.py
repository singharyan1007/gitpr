import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_bad_signature_rejected():
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post(
                "/api/webhook", content=b"{}", headers={"X-Hub-Signature-256": "sha256=bad"}
            )
            assert resp.status_code == 401