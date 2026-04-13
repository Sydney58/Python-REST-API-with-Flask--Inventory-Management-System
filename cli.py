import requests

# the flask server needs to be running for this to work
BASE_URL = "http://127.0.0.1:5000"


# prints one inventory item in a nice format
def print_item(item):
    print()
    print(f"  ID          : {item.get('id')}")
    print(f"  Product Name: {item.get('product_name')}")
    print(f"  Brand       : {item.get('brands')}")
    print(f"  Barcode     : {item.get('barcode')}")
    print(f"  Category    : {item.get('category')}")
    print(f"  Price       : ${item.get('price')}")
    print(f"  Stock       : {item.get('stock_quantity')} units")
    print(f"  Ingredients : {item.get('ingredients_text')}")
    print()


def view_all_inventory():
    try:
        response = requests.get(f"{BASE_URL}/inventory")
        items = response.json()

        if len(items) == 0:
            print("No items in inventory.")
            return

        print("\n" + "-" * 50)
        print("INVENTORY LIST")
        print("-" * 50)

        for item in items:
            print_item(item)
            print("-" * 50)

    except requests.exceptions.ConnectionError:
        print("Could not connect. Make sure app.py is running first!")


def view_single_item():
    item_id = input("Enter item ID: ")

    # make sure the user typed a number
    if not item_id.isdigit():
        print("Please enter a valid number.")
        return

    try:
        response = requests.get(f"{BASE_URL}/inventory/{item_id}")

        if response.status_code == 200:
            print_item(response.json())
        else:
            print(f"Error: {response.json().get('error')}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to the server.")


def add_item():
    print("\nEnter the new item details below.")
    print("(just press Enter to skip optional fields)\n")

    product_name = input("Product Name (required): ").strip()

    if product_name == "":
        print("Product name can't be empty!")
        return

    barcode = input("Barcode: ").strip()
    if barcode == "":
        barcode = "N/A"

    brands = input("Brand: ").strip()
    if brands == "":
        brands = "Unknown"

    category = input("Category: ").strip()
    if category == "":
        category = "Uncategorized"

    ingredients = input("Ingredients: ").strip()
    if ingredients == "":
        ingredients = "N/A"

    # handle bad price input
    price_input = input("Price (e.g. 2.99): ").strip()
    try:
        price = float(price_input)
    except ValueError:
        print("Invalid price, setting to 0.")
        price = 0.0

    # handle bad stock input
    stock_input = input("Stock Quantity: ").strip()
    try:
        stock = int(stock_input)
    except ValueError:
        print("Invalid quantity, setting to 0.")
        stock = 0

    # send the data to the API
    new_item = {
        "product_name": product_name,
        "barcode": barcode,
        "brands": brands,
        "category": category,
        "ingredients_text": ingredients,
        "price": price,
        "stock_quantity": stock
    }

    try:
        response = requests.post(f"{BASE_URL}/inventory", json=new_item)

        if response.status_code == 201:
            print("\nItem added successfully!")
            print_item(response.json())
        else:
            print(f"Error: {response.json().get('error')}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to the server.")


def update_item():
    item_id = input("Enter item ID to update: ")

    if not item_id.isdigit():
        print("Please enter a valid number.")
        return

    print("\nEnter new values (press Enter to skip):")

    updates = {}

    new_price = input("New price: ").strip()
    if new_price != "":
        try:
            updates["price"] = float(new_price)
        except ValueError:
            print("Invalid price, skipping.")

    new_stock = input("New stock quantity: ").strip()
    if new_stock != "":
        try:
            updates["stock_quantity"] = int(new_stock)
        except ValueError:
            print("Invalid quantity, skipping.")

    new_name = input("New product name: ").strip()
    if new_name != "":
        updates["product_name"] = new_name

    new_category = input("New category: ").strip()
    if new_category != "":
        updates["category"] = new_category

    if len(updates) == 0:
        print("Nothing to update.")
        return

    try:
        response = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=updates)

        if response.status_code == 200:
            print("\nItem updated!")
            print_item(response.json())
        else:
            print(f"Error: {response.json().get('error')}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to the server.")


def delete_item():
    item_id = input("Enter item ID to delete: ")

    if not item_id.isdigit():
        print("Please enter a valid number.")
        return

    # double check before deleting
    confirm = input(f"Are you sure you want to delete item {item_id}? (yes/no): ").strip()

    if confirm != "yes":
        print("Cancelled.")
        return

    try:
        response = requests.delete(f"{BASE_URL}/inventory/{item_id}")

        if response.status_code == 200:
            print(response.json().get("message"))
        else:
            print(f"Error: {response.json().get('error')}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to the server.")


def search_external_api():
    print("\nSearch OpenFoodFacts")
    print("1. Search by barcode")
    print("2. Search by product name")

    choice = input("Choose an option: ").strip()

    results = []

    try:
        if choice == "1":
            barcode = input("Enter barcode number: ").strip()
            response = requests.get(f"{BASE_URL}/inventory/search/barcode/{barcode}")

            if response.status_code == 200:
                # put the single result in a list so we can reuse the display code below
                results = [response.json()]
            else:
                print(f"Error: {response.json().get('error')}")
                return

        elif choice == "2":
            name = input("Enter product name to search: ").strip()
            response = requests.get(f"{BASE_URL}/inventory/search/name/{name}")

            if response.status_code == 200:
                results = response.json()
            else:
                print(f"Error: {response.json().get('error')}")
                return

        else:
            print("Invalid option.")
            return

    except requests.exceptions.ConnectionError:
        print("Could not connect to the server.")
        return

    # show what we found
    print(f"\nFound {len(results)} result(s):\n")
    for i, product in enumerate(results, 1):
        print(f"  [{i}] {product.get('product_name')} - {product.get('brands')}")
        print(f"      Barcode : {product.get('barcode')}")
        print(f"      Category: {product.get('category')}")
        print()

    # ask if the user wants to add one to inventory
    add_it = input("Add one of these to inventory? Enter the number or 0 to cancel: ").strip()

    if not add_it.isdigit():
        return

    add_index = int(add_it)

    if add_index == 0 or add_index > len(results):
        return

    # grab the product they picked
    selected = results[add_index - 1]

    try:
        price = float(input("Set a price: $").strip() or 0)
    except ValueError:
        price = 0.0

    try:
        stock = int(input("Set stock quantity: ").strip() or 0)
    except ValueError:
        stock = 0

    selected["price"] = price
    selected["stock_quantity"] = stock

    try:
        response = requests.post(f"{BASE_URL}/inventory", json=selected)

        if response.status_code == 201:
            print("\nAdded to inventory!")
            print_item(response.json())
        else:
            print(f"Error: {response.json().get('error')}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to the server.")


# main loop - keeps showing the menu until the user exits
def main():
    print("\n====================================")
    print("  Inventory Management System")
    print("====================================")

    while True:
        print("\nWhat do you want to do?")
        print("1. View all inventory")
        print("2. View a single item")
        print("3. Add a new item")
        print("4. Update an item")
        print("5. Delete an item")
        print("6. Search OpenFoodFacts API")
        print("7. Exit")

        choice = input("\nEnter choice: ").strip()

        if choice == "1":
            view_all_inventory()
        elif choice == "2":
            view_single_item()
        elif choice == "3":
            add_item()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            search_external_api()
        elif choice == "7":
            print("Bye!")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
