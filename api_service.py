import requests


BASE_URL = "https://world.openfoodfacts.org"


def fetch_product_by_barcode(barcode):
    url = f"{BASE_URL}/api/v0/product/{barcode}.json"

    try:
        # added timeout=5 because it was hanging when the api was slow
        response = requests.get(url, timeout=5)
        data = response.json()

        # the api returns status=1 if it found the product
        if data.get("status") == 1:
            product = data["product"]

            # pull out just the fields we care about
            return {
                "barcode": barcode,
                "product_name": product.get("product_name", "Unknown"),
                "brands": product.get("brands", "Unknown"),
                "ingredients_text": product.get("ingredients_text", "N/A"),
                "category": product.get("categories", "Uncategorized").split(",")[0].strip()
            }
        else:
            # product not found
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to OpenFoodFacts: {e}")
        return None


def search_product_by_name(name):
    url = f"{BASE_URL}/cgi/search.pl"

    # these are the search parameters the api expects
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 5  # only get 5 results
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        results = []

        for product in data.get("products", []):
            # some products don't have a category so we handle that here
            if product.get("categories"):
                category = product.get("categories").split(",")[0].strip()
            else:
                category = "Uncategorized"

            results.append({
                "barcode": product.get("code", "N/A"),
                "product_name": product.get("product_name", "Unknown"),
                "brands": product.get("brands", "Unknown"),
                "ingredients_text": product.get("ingredients_text", "N/A"),
                "category": category
            })

        return results

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to OpenFoodFacts: {e}")
        return []
