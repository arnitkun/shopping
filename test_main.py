import pytest
from loguru import logger


# @pytest.fixture
# def client():
#     return TestClient(app)


import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from main import app, DB


@pytest.fixture
def mock_db():
    with patch.object(DB, 'products', AsyncMock()) as mock_products, \
         patch.object(DB, 'orders', AsyncMock()) as mock_orders:

        mock_products.find.return_value = [
            {
                "_id": "676083af343096de589f0b6c",
                "name": "Product 1",
                "description": "Description of Product 1",
                "price": 10.0,
                "stock": 100,
            }
        ]
        mock_products.insert_one.return_value = "123"
        mock_products.find_one.return_value = {
            "_id": "676083af343096de589f0b6c",
            "name": "Product 1",
            "description": "Description of Product 1",
            "price": 10.0,
            "stock": 100,
        }
        mock_products.update_one.return_value = None

        mock_orders.insert_one.return_value = "order123"  # Correct return value

        yield DB(mongo_url="mongodb://localhost", db_name="ecommerce")



@pytest.fixture
def client(mock_db):
    app.state.db = mock_db
    return TestClient(app)



@pytest.mark.asyncio
async def test_add_product(client, mock_db):
    product_data = {
        "name": "Product 1",
        "description": "Description of Product 1",
        "price": 10.0,
        "stock": 100
    }

    response = client.post("/products", json=product_data)

    assert response.status_code == 200
    assert response.json() == {"message": "Product added successfully!", "id": "123"}


@pytest.mark.asyncio
async def test_get_products(client, mock_db):
    mock_db.products.find.return_value = [
        {"_id": "676083af343096de589f0b6c", "description": "something", "name": "Product 1", "price": 10.0, "stock": 100}
    ]

    response = client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Product 1"
    assert response.json()[0]["description"] == "something"


@pytest.mark.asyncio
async def test_place_order(client, mock_db):
    order_data = {
        "products": [
            {"product_id": "676083af343096de589f0b6c", "quantity": 2}
        ]
    }

    mock_db.products.find_one.return_value = {"_id": "676083af343096de589f0b6c", "name": "Product 1", "price": 10.0, "stock": 100}

    response = client.post("/orders", json=order_data)

    assert response.status_code == 200
    assert response.json() == {"message": "Order placed successfully!", "order_id": "order123"}


@pytest.mark.asyncio
async def test_order_product_not_found(client, mock_db):
    order_data = {
        "products": [
            {"product_id": "676083af343096de589f0b6d", "quantity": 1}
        ]
    }

    mock_db.products.find_one.return_value = None

    response = client.post("/orders", json=order_data)

    assert response.status_code == 404
    logger.info(response.json())
    assert response.json() == {"detail": "Product with id: 676083af343096de589f0b6d not found."}


@pytest.mark.asyncio
async def test_order_insufficient_stock(client, mock_db):
    order_data = {
        "products": [
            {"product_id": "676083af343096de589f0b6c", "quantity": 200}
        ]
    }

    mock_db.products.find_one.return_value = {"_id": "676083af343096de589f0b6c", "name": "Product 1", "price": 10.0, "stock": 100}

    response = client.post("/orders", json=order_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "Insufficient stock for product Product 1."}
