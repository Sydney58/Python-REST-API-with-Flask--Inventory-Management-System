
inventory = [
    {
        "id": 1,
        "barcode": "0041570056530",
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "ingredients_text": "Filtered water, almonds, cane sugar, vitamin and mineral blend",
        "category": "Beverages",
        "price": 4.99,
        "stock_quantity": 50
    },
    {
        "id": 2,
        "barcode": "0038000845574",
        "product_name": "Frosted Flakes",
        "brands": "Kellogg's",
        "ingredients_text": "Milled corn, sugar, malt flavoring, iron, niacinamide",
        "category": "Cereals",
        "price": 3.49,
        "stock_quantity": 30
    },
    {
        "id": 3,
        "barcode": "0016000275270",
        "product_name": "Cheerios",
        "brands": "General Mills",
        "ingredients_text": "Whole grain oats, modified corn starch, sugar, salt, calcium carbonate",
        "category": "Cereals",
        "price": 4.19,
        "stock_quantity": 45
    },
    {
        "id": 4,
        "barcode": "0070470003030",
        "product_name": "Peanut Butter",
        "brands": "Jif",
        "ingredients_text": "Roasted peanuts, sugar, contains 2% or less of molasses, fully hydrogenated vegetable oils",
        "category": "Spreads",
        "price": 5.99,
        "stock_quantity": 25
    },
    {
        "id": 5,
        "barcode": "0085239012321",
        "product_name": "Greek Yogurt",
        "brands": "Chobani",
        "ingredients_text": "Cultured nonfat milk, evaporated cane juice, natural flavors, fruit pectin",
        "category": "Dairy",
        "price": 1.99,
        "stock_quantity": 60
    }
]

# this keeps track of what id to assign next
next_id = 6

def get_next_id():
    global next_id
    id_to_use = next_id
    next_id += 1
    return id_to_use
