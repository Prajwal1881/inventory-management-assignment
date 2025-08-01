```
# Part 3: API Implemented for Stock Alert

```
@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def low_stock_alerts(company_id):
    try:
        alerts = []
        
        # Query products with low stock
        results = db.session.query(
            Product.id, Product.name, Product.sku,
            Inventory.warehouse_id, Warehouse.name.label('warehouse_name'),
            Inventory.quantity, Product.low_stock_threshold,
            Supplier.id.label('supplier_id'), Supplier.name.label('supplier_name'),
            Supplier.contact_email
        ).join(Inventory, Inventory.product_id == Product.id) \
         .join(Warehouse, Warehouse.id == Inventory.warehouse_id) \
         .join(Product_Suppliers, Product_Suppliers.product_id == Product.id) \
         .join(Supplier, Supplier.id == Product_Suppliers.supplier_id) \
         .filter(Warehouse.company_id == company_id) \
         .filter(Inventory.quantity < Product.low_stock_threshold) \
         .all()
        
        for r in results:
            # Estimate days until stockout (simple assumption)
            avg_daily_sales = 1  # TODO: compute from logs
            days_until_stockout = r.quantity // avg_daily_sales if avg_daily_sales > 0 else None
            
            alerts.append({
                "product_id": r.id,
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
