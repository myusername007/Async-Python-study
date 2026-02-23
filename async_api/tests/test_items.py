import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.anyio
async def test_create_item():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/items", json={
            "title": "Test item",
            "description": "Test desc"
        })
    assert response.status_code == 201
    assert response.json()["title"] == "Test item"

@pytest.mark.anyio
async def test_get_items():
    #create item
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/items", json={
            "title": "Test item",
            "description": "Test desc"
        })
    assert response.status_code == 201
    assert response.json()["title"] == "Test item"

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    )as client:
        get_response = await client.get("/items")
        assert get_response.status_code == 200
        assert len(get_response.json()) >= 1
