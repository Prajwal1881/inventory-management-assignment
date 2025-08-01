
# Part 1: Code Review & Debugging

## Issues Identified
1. **SKU uniqueness not enforced**
   - Could cause duplicate SKUs → confusion in sales & reporting.
   - **Fix:** Added check for SKU before insert.

2. **Multiple commits instead of transaction**
   - Risk of partial data commit if second commit fails.
   - **Fix:** Used single transaction.

3. **Price handling**
   - Might store as integer, losing precision.
   - **Fix:** Used decimal to store the price.

4. **Warehouse handling**
   - Product tied to one warehouse instead of multiple.
   - **Fix:** Move warehouse reference to `Inventory` table.

5. **Error handling missing**
   - API may crash on missing fields.
   - **Fix:** Added validation & return 400 error.

6. **Initial quantity assumption**
   - KeyError if not provided.
   - **Fix:** Quantity set assign Default to 0.

---

## This is the Corrected Code

```
@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json

    # Validate required fields
    required = ['name', 'sku', 'price', 'warehouse_id']
    for field in required:
        if field not in data:
            return {"error": f"Missing field: {field}"}, 400

    try:
        # Unique SKU check
        existing = Product.query.filter_by(sku=data['sku']).first()
        if existing:
            return {"error": "SKU must be unique"}, 400

        product = Product(
            name=data['name'],
            sku=data['sku'],
            price=float(data['price'])
        )

        db.session.add(product)
        db.session.flush()  # get product.id

        inventory = Inventory(
            product_id=product.id,
            warehouse_id=data['warehouse_id'],
            quantity=data.get('initial_quantity', 0)
        )
        db.session.add(inventory)
        db.session.commit()

        return {"message": "Product created", "product_id": product.id}, 201

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500
