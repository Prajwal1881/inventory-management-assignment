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
## Design Decisions and Justifications

### Primary Keys
- Every table has a surrogate key (`id`) for simplicity and consistency.
- Ensures easier joins and avoids composite PKs for readability.

### Foreign Keys
- Enforce referential integrity (e.g., `warehouse_id` in Inventory must exist in Warehouses).
- Prevents orphan records.

### Indexes
- **Products.sku → Unique Index**
  - Ensures SKU uniqueness across platform.
  - Optimizes lookups since SKU will be frequently searched.
- **Inventory (warehouse_id, product_id) → Composite Index**
  - Improves stock queries per warehouse and product.
- **Inventory_Logs.inventory_id**
  - Needed for quick retrieval of sales history when computing recent activity.

### Constraints
- **CHECK (quantity >= 0) on Inventory**
  - Prevents negative stock values.
- **NOT NULL on critical fields** (`name`, `sku`, `price`)  
  - Ensures data completeness.
- **Unique constraint on Products.sku**
  - Business rule enforcement for unique product identifiers.

### Normalization
- Schema is in 3rd Normal Form (3NF).
- Avoids duplication: Suppliers stored separately, Products reusable across warehouses.

### Auditability
- **Inventory_Logs** tracks every stock change.
- Allows historical reporting and future analytics (e.g., sales trends).

### Scalability
- Separation of **Products**, **Warehouses**, and **Inventory** supports companies with multiple warehouses.
- Many-to-many structure for **Product ↔ Supplier** allows flexible supplier management.

---

## Gaps / Questions
- Should inventory logs track user who made changes?
- Should bundles have dynamic or fixed pricing?
- Should thresholds be customizable by warehouse or product only?
- Should suppliers be global or company-specific?

