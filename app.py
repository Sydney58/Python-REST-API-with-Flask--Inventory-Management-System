from flask import Flask, jsonify, request
import database as db
from api_service import fetch_product_by_barcode, search_product_by_name

app = Flask(__name__)


# loops through the inventory list and returns the item with the matching id
# returns None if nothing is found
def find_item(item_id):
    for item in db.inventory:
        if item["id"] == item_id:
            return item
    return None


# GET all items in inventory
@app.route("/inventory", methods=["GET"])
def get_all_items():
    return jsonify(db.inventory), 200


# GET a single item by its id
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)

    # if nothing was found, return a 404
    if item is None:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404

    return jsonify(item), 200


# POST - add a new item to inventory
@app.route("/inventory", methods=["POST"])
def add_item():
    data = request.get_json()

    # make sure the request actually has data and a product name
    if not data or "product_name" not in data:
        return jsonify({"error": "product_name is required"}), 400

    # build the new item - use .get() so missing fields get a default value
    new_item = {
        "id": db.get_next_id(),
        "barcode": data.get("barcode", "N/A"),
        "product_name": data["product_name"],
        "brands": data.get("brands", "Unknown"),
        "ingredients_text": data.get("ingredients_text", "N/A"),
        "category": data.get("category", "Uncategorized"),
        "price": data.get("price", 0.0),
        "stock_quantity": data.get("stock_quantity", 0)
    }

    db.inventory.append(new_item)
    return jsonify(new_item), 201


# PATCH - update an existing item (only the fields that are sent)
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "No update data provided"}), 400

    # only let the user update these specific fields
    allowed_fields = ["product_name", "brands", "ingredients_text", "category", "price", "stock_quantity", "barcode"]

    for field in allowed_fields:
        if field in data:
            item[field] = data[field]

    return jsonify(item), 200


# DELETE - remove an item from the inventory
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)

    if item is None:
        return jsonify({"error": f"Item with id {item_id} not found"}), 404

    db.inventory.remove(item)
    return jsonify({"message": f"Item {item_id} deleted successfully"}), 200


# GET - search OpenFoodFacts by barcode number
@app.route("/inventory/search/barcode/<barcode>", methods=["GET"])
def search_by_barcode(barcode):
    product = fetch_product_by_barcode(barcode)

    if product is None:
        return jsonify({"error": f"No product found for barcode {barcode}"}), 404

    return jsonify(product), 200


# GET - search OpenFoodFacts by product name
@app.route("/inventory/search/name/<name>", methods=["GET"])
def search_by_name(name):
    results = search_product_by_name(name)

    if not results:
        return jsonify({"error": f"No products found for '{name}'"}), 404

    return jsonify(results), 200


if __name__ == "__main__":
    # debug=True so we can see errors while developing
    app.run(debug=True)
