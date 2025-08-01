### PART2_DatabaseDesign.md

# Part 2: Database Design

## Tables

### Companies
- id (PK)
- name
- created_at

### Warehouses
- id (PK)
- company_id (FK → Companies.id)
- name
- location

### Products
- id (PK)
- name
- sku (Unique)
- price (Decimal)
- low_stock_threshold (Integer)

### Inventory
- id (PK)
- product_id (FK → Products.id)
- warehouse_id (FK → Warehouses.id)
- quantity (Integer, >=0)
- updated_at (Timestamp)

### Suppliers
- id (PK)
- name
- contact_email

### Product_Suppliers
- id (PK)
- product_id (FK → Products.id)
- supplier_id (FK → Suppliers.id)

### Inventory_Logs
- id (PK)
- inventory_id (FK → Inventory.id)
- change (Integer)
- reason (Text)
- changed_at (Timestamp)

### Bundles
- id (PK)
- bundle_product_id (FK → Products.id)
- component_product_id (FK → Products.id)
- quantity (Integer)

---

## Relationships (Text-based ERD)
- Company → Warehouses (1:N)
- Product → Inventory (1:N)
- Warehouse → Inventory (1:N)
- Product ↔ Supplier (M:N via Product_Suppliers)
- Inventory → Inventory_Logs (1:N)
- Product ↔ Product (Bundles table defines M:N for bundles)

---

## Gaps / Questions
- Should inventory logs track user who made changes?
- Should bundles have dynamic or fixed pricing?
- Should thresholds be customizable by warehouse or product only?
- Should suppliers be global or company-specific?

