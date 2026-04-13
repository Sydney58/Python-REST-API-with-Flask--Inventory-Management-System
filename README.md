# Inventory Management System

This is a REST API built with Flask for managing a store's inventory. It also connects to the OpenFoodFacts API so you can look up real product info by barcode or name. There's also a CLI tool so you can interact with it from the terminal.

---

## How to run it

**Step 1 - clone the repo and go into the folder**
```bash
git clone <your-repo-url>
cd inventory-management-system
```

**Step 2 - create a virtual environment (recommended)**
```bash
python -m venv venv
source venv/bin/activate    # Mac/Linux
venv\Scripts\activate       # Windows
```

**Step 3 - install the requirements**
```bash
pip install -r requirements.txt
```

**Step 4 - start the Flask server**
```bash
python app.py
```

The server will run at `http://127.0.0.1:5000`

---

## API Endpoints

| Method | Route | What it does |
|--------|-------|--------------|
| GET | `/inventory` | get all items |
| GET | `/inventory/<id>` | get one item by id |
| POST | `/inventory` | add a new item |
| PATCH | `/inventory/<id>` | update an item |
| DELETE | `/inventory/<id>` | delete an item |
| GET | `/inventory/search/barcode/<barcode>` | look up a product on OpenFoodFacts |
| GET | `/inventory/search/name/<name>` | search OpenFoodFacts by name |

### Some example curl commands

```bash
# get everything
curl http://127.0.0.1:5000/inventory

# get item with id 1
curl http://127.0.0.1:5000/inventory/1

# add a new item
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Orange Juice", "brands": "Tropicana", "price": 3.99, "stock_quantity": 20}'

# update the price and stock of item 1
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"price": 5.49, "stock_quantity": 100}'

# delete item 2
curl -X DELETE http://127.0.0.1:5000/inventory/2

# search by barcode
curl http://127.0.0.1:5000/inventory/search/barcode/0041570056530
```

---

## Using the CLI

Make sure the Flask server is running first. Then open a second terminal and run:

```bash
python cli.py
```

It'll show you a menu where you can view, add, update, delete, and search for products.

---

## Running the tests

```bash
pytest tests/ -v
```

The tests use `unittest.mock` to fake the OpenFoodFacts API responses so they don't need an internet connection.

---

## Notes

- The "database" is just a Python list in `database.py` - data resets every time the server restarts
- OpenFoodFacts is completely free and doesn't need an API key
- Run the server with `python app.py` before using the CLI
