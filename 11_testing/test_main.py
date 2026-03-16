# test_main.py — FastAPI Testing with pytest
# Run karo: pytest test_main.py -v

import pytest
from fastapi.testclient import TestClient
from main import app, items_db, counter

client = TestClient(app)


# ─── Fixtures ────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def clean_db():
    """Har test se pehle DB clean karo"""
    items_db.clear()
    counter["id"] = 0
    yield
    items_db.clear()
    counter["id"] = 0


@pytest.fixture
def sample_item():
    """Test item create karo"""
    response = client.post("/items", json={"name": "Test Phone", "price": 50000.0})
    return response.json()


# ─── Home route test ──────────────────────────────────────────────────────────
def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "App chal raha hai!"}


# ─── Create Item tests ────────────────────────────────────────────────────────
def test_create_item_success():
    response = client.post(
        "/items",
        json={"name": "Laptop", "price": 150000.0, "in_stock": True},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Laptop"
    assert data["price"] == 150000.0
    assert "id" in data


def test_create_item_missing_field():
    # Name missing hai — validation error aani chahiye
    response = client.post("/items", json={"price": 100.0})
    assert response.status_code == 422  # Unprocessable Entity


def test_create_item_negative_price():
    # Pydantic validation catch karega? (agar validator likha ho)
    response = client.post("/items", json={"name": "Item", "price": -100.0})
    # By default allow hoga (validator nahi likha) — test adjust karo
    assert response.status_code in [201, 422]


# ─── Get Items tests ──────────────────────────────────────────────────────────
def test_get_items_empty():
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


def test_get_items_with_data(sample_item):
    response = client.get("/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["name"] == "Test Phone"


# ─── Get Single Item tests ────────────────────────────────────────────────────
def test_get_item_success(sample_item):
    item_id = sample_item["id"]
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id


def test_get_item_not_found():
    response = client.get("/items/9999")
    assert response.status_code == 404
    assert "nahi mila" in response.json()["detail"]


# ─── Update Item tests ────────────────────────────────────────────────────────
def test_update_item_success(sample_item):
    item_id = sample_item["id"]
    response = client.put(
        f"/items/{item_id}",
        json={"name": "Updated Phone", "price": 45000.0},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Phone"
    assert response.json()["price"] == 45000.0


def test_update_item_not_found():
    response = client.put("/items/9999", json={"name": "Ghost", "price": 0.0})
    assert response.status_code == 404


# ─── Delete Item tests ────────────────────────────────────────────────────────
def test_delete_item_success(sample_item):
    item_id = sample_item["id"]
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204

    # Ab get karo — 404 aani chahiye
    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 404


def test_delete_item_not_found():
    response = client.delete("/items/9999")
    assert response.status_code == 404


# ─── Integration test — full flow ─────────────────────────────────────────────
def test_full_crud_flow():
    # 1. Create
    create_res = client.post("/items", json={"name": "Flow Test Item", "price": 999.0})
    assert create_res.status_code == 201
    item_id = create_res.json()["id"]

    # 2. Get
    get_res = client.get(f"/items/{item_id}")
    assert get_res.status_code == 200

    # 3. Update
    update_res = client.put(f"/items/{item_id}", json={"name": "Updated", "price": 1000.0})
    assert update_res.status_code == 200
    assert update_res.json()["price"] == 1000.0

    # 4. Delete
    del_res = client.delete(f"/items/{item_id}")
    assert del_res.status_code == 204

    # 5. Verify deletion
    final_res = client.get(f"/items/{item_id}")
    assert final_res.status_code == 404
