import pytest
from unittest.mock import patch, MagicMock
import database as db


# reset the fake database before each test so tests don't interfere with each other
@pytest.fixture(autouse=True)
def reset_database():
    db.inventory.clear()
    db.inventory.extend([
        {
            "id": 1,
            "barcode": "0041570056530",
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds, cane sugar",
            "category": "Beverages",
            "price": 4.99,
            "stock_quantity": 50
        },
        {
            "id": 2,
            "barcode": "0038000845574",
            "product_name": "Frosted Flakes",
            "brands": "Kellogg's",
            "ingredients_text": "Milled corn, sugar, malt flavoring",
            "category": "Cereals",
            "price": 3.49,
            "stock_quantity": 30
        }
    ])
    db.next_id = 3


# create a test version of the flask app
@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---- tests for GET /inventory ----

def test_get_all_items_returns_200(client):
    response = client.get("/inventory")
    assert response.status_code == 200

def test_get_all_items_returns_a_list(client):
    response = client.get("/inventory")
    assert isinstance(response.get_json(), list)

def test_get_all_items_has_2_items(client):
    # we added 2 items in the fixture so there should be 2
    response = client.get("/inventory")
    assert len(response.get_json()) == 2

def test_each_item_has_the_right_fields(client):
    item = client.get("/inventory").get_json()[0]
    assert "id" in item
    assert "product_name" in item
    assert "price" in item
    assert "stock_quantity" in item


# ---- tests for GET /inventory/<id> ----

def test_get_one_item_returns_200(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200

def test_get_one_item_returns_the_right_product(client):
    response = client.get("/inventory/1")
    assert response.get_json()["product_name"] == "Organic Almond Milk"

def test_get_item_that_doesnt_exist_returns_404(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404

def test_404_response_has_an_error_message(client):
    response = client.get("/inventory/999")
    assert "error" in response.get_json()


# ---- tests for POST /inventory ----

def test_adding_an_item_returns_201(client):
    new_item = {"product_name": "Test Product", "price": 1.99, "stock_quantity": 10}
    response = client.post("/inventory", json=new_item)
    assert response.status_code == 201

def test_added_item_shows_up_when_you_get_all(client):
    client.post("/inventory", json={"product_name": "New Cereal", "price": 2.99, "stock_quantity": 20})
    all_items = client.get("/inventory").get_json()
    names = [item["product_name"] for item in all_items]
    assert "New Cereal" in names

def test_posting_without_product_name_returns_400(client):
    response = client.post("/inventory", json={"price": 1.99})
    assert response.status_code == 400

def test_new_item_gets_an_id(client):
    response = client.post("/inventory", json={"product_name": "Something"})
    assert "id" in response.get_json()

def test_missing_fields_get_default_values(client):
    response = client.post("/inventory", json={"product_name": "Plain Item"})
    data = response.get_json()
    assert data["brands"] == "Unknown"
    assert data["category"] == "Uncategorized"


# ---- tests for PATCH /inventory/<id> ----

def test_updating_an_item_returns_200(client):
    response = client.patch("/inventory/1", json={"price": 9.99})
    assert response.status_code == 200

def test_price_actually_changes_after_update(client):
    client.patch("/inventory/1", json={"price": 9.99})
    updated = client.get("/inventory/1").get_json()
    assert updated["price"] == 9.99

def test_stock_quantity_changes_after_update(client):
    client.patch("/inventory/2", json={"stock_quantity": 100})
    updated = client.get("/inventory/2").get_json()
    assert updated["stock_quantity"] == 100

def test_updating_item_that_doesnt_exist_returns_404(client):
    response = client.patch("/inventory/999", json={"price": 1.0})
    assert response.status_code == 404

def test_sending_empty_update_returns_400(client):
    response = client.patch("/inventory/1", json={})
    assert response.status_code == 400

def test_other_fields_stay_the_same_after_partial_update(client):
    client.patch("/inventory/1", json={"price": 1.00})
    # product name should still be the same
    assert client.get("/inventory/1").get_json()["product_name"] == "Organic Almond Milk"


# ---- tests for DELETE /inventory/<id> ----

def test_deleting_an_item_returns_200(client):
    response = client.delete("/inventory/1")
    assert response.status_code == 200

def test_deleted_item_is_actually_gone(client):
    client.delete("/inventory/1")
    response = client.get("/inventory/1")
    assert response.status_code == 404

def test_inventory_has_one_less_item_after_delete(client):
    client.delete("/inventory/1")
    assert len(client.get("/inventory").get_json()) == 1

def test_deleting_item_that_doesnt_exist_returns_404(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404

def test_delete_response_has_a_message(client):
    response = client.delete("/inventory/2")
    assert "message" in response.get_json()


# ---- tests for the OpenFoodFacts search routes ----
# we mock the API calls so we don't actually hit the internet during tests

@patch("app.fetch_product_by_barcode")
def test_barcode_search_returns_200_when_found(mock_fetch, client):
    mock_fetch.return_value = {
        "barcode": "0041570056530",
        "product_name": "Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Water, almonds",
        "category": "Beverages"
    }
    response = client.get("/inventory/search/barcode/0041570056530")
    assert response.status_code == 200

@patch("app.fetch_product_by_barcode")
def test_barcode_search_returns_the_product_data(mock_fetch, client):
    mock_fetch.return_value = {
        "barcode": "0041570056530",
        "product_name": "Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Water, almonds",
        "category": "Beverages"
    }
    data = client.get("/inventory/search/barcode/0041570056530").get_json()
    assert data["product_name"] == "Almond Milk"

@patch("app.fetch_product_by_barcode")
def test_barcode_search_returns_404_when_not_found(mock_fetch, client):
    mock_fetch.return_value = None
    response = client.get("/inventory/search/barcode/0000000000000")
    assert response.status_code == 404

@patch("app.search_product_by_name")
def test_name_search_returns_200(mock_search, client):
    mock_search.return_value = [
        {"barcode": "123", "product_name": "Cheerios", "brands": "General Mills",
         "ingredients_text": "Oats", "category": "Cereals"}
    ]
    response = client.get("/inventory/search/name/cheerios")
    assert response.status_code == 200

@patch("app.search_product_by_name")
def test_name_search_returns_a_list(mock_search, client):
    mock_search.return_value = [
        {"barcode": "123", "product_name": "Cheerios", "brands": "General Mills",
         "ingredients_text": "Oats", "category": "Cereals"}
    ]
    assert isinstance(client.get("/inventory/search/name/cheerios").get_json(), list)

@patch("app.search_product_by_name")
def test_name_search_returns_404_when_nothing_found(mock_search, client):
    mock_search.return_value = []
    response = client.get("/inventory/search/name/xyznotaproduct")
    assert response.status_code == 404


# ---- tests for api_service.py ----
# these test the functions that call OpenFoodFacts directly

@patch("api_service.requests.get")
def test_fetch_by_barcode_works_when_product_exists(mock_get):
    # fake a successful API response
    mock_get.return_value = MagicMock(json=lambda: {
        "status": 1,
        "product": {
            "product_name": "Test Milk",
            "brands": "TestBrand",
            "ingredients_text": "Water, milk",
            "categories": "Dairy, Beverages"
        }
    })

    from api_service import fetch_product_by_barcode
    result = fetch_product_by_barcode("1234567890")

    assert result is not None
    assert result["product_name"] == "Test Milk"
    assert result["brands"] == "TestBrand"

@patch("api_service.requests.get")
def test_fetch_by_barcode_returns_none_if_not_found(mock_get):
    # fake a "not found" response (status=0)
    mock_get.return_value = MagicMock(json=lambda: {"status": 0})

    from api_service import fetch_product_by_barcode
    result = fetch_product_by_barcode("0000000000")
    assert result is None

@patch("api_service.requests.get")
def test_search_by_name_returns_list_of_products(mock_get):
    mock_get.return_value = MagicMock(json=lambda: {
        "products": [
            {"code": "111", "product_name": "Oat Milk", "brands": "Oatly",
             "ingredients_text": "Oats, water", "categories": "Beverages"}
        ]
    })

    from api_service import search_product_by_name
    results = search_product_by_name("oat milk")

    assert len(results) == 1
    assert results[0]["product_name"] == "Oat Milk"

@patch("api_service.requests.get")
def test_search_by_name_returns_empty_list_when_nothing_found(mock_get):
    mock_get.return_value = MagicMock(json=lambda: {"products": []})

    from api_service import search_product_by_name
    assert search_product_by_name("xyzabc") == []

@patch("api_service.requests.get")
def test_fetch_by_barcode_returns_none_on_connection_error(mock_get):
    # simulate the API being down
    import requests as req
    mock_get.side_effect = req.exceptions.RequestException("Connection failed")

    from api_service import fetch_product_by_barcode
    result = fetch_product_by_barcode("1234567890")
    assert result is None
