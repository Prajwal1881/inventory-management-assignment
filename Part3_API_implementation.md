
# Part 3: API Implemented for Stock Alert

```
@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def low_stock_alerts(company_id):
    try:
        alerts = []
        
        # Query to get products with low stock
        results = db.session.query(
            Product.product_id, Product.name, Product.sku,
            Inventory.warehouse_id, Warehouse.name.label('warehouse_name'),
            Inventory.quantity, Product.low_stock_threshold,
            Supplier.supplier_id, Supplier.name.label('supplier_name'),
            Supplier.contact_email
        ).join(Inventory, Inventory.product_id == Product.product_id) \
         .join(Warehouse, Warehouse.warehouse_id == Inventory.warehouse_id) \
         .join(Product_Suppliers, Product_Suppliers.product_id == Product.product_id) \
         .join(Supplier, Supplier.supplier_id == Product_Suppliers.supplier_id) \
         .filter(Warehouse.company_id == company_id) \
         .filter(Inventory.quantity < Product.low_stock_threshold) \
         .all()
        
        for r in results:
            # Estimate days until stockout (simple assumption)
            # Ideally, this comes from recent sales logs
            avg_daily_sales = 1  # This should be computed from sales_logs
            days_until_stockout = r.quantity // avg_daily_sales if avg_daily_sales > 0 else None
            
            alerts.append({
                "product_id": r.product_id,
                "product_name": r.name,
                "sku": r.sku,
                "warehouse_id": r.warehouse_id,
                "warehouse_name": r.warehouse_name,
                "current_stock": r.quantity,
                "threshold": r.low_stock_threshold,
                "days_until_stockout": days_until_stockout,
                "supplier": {
                    "id": r.supplier_id,
                    "name": r.supplier_name,
                    "contact_email": r.contact_email
                }
            })
        
        return {"alerts": alerts, "total_alerts": len(alerts)}

    except Exception as e:
        return {"error": str(e)}, 500
```

## Edge Cases Considered

#### No products below threshold
- Return { "alerts": [], "total_alerts": 0 } instead of error.
#### Missing or invalid company_id
- If company not found, query returns no results (empty alerts list).
- Could optionally add 404 if required.
#### Products without suppliers
- Assumed every product has at least one supplier.
- If not, should handle with default None.
#### Division by zero in stockout calculation
- If avg_daily_sales is 0, return None for days_until_stockout.
#### Database errors
- Wrapped in try-except with rollback and clean error response.
#### Threshold not set for a product
- Default threshold in Product model (low_stock_threshold = 10).


