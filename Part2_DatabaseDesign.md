# Part 2: Database Design

## Tables

### Companies
```
CREATE TABLE Companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
#### Attributes
- company_id → INT, PK
- name → VARCHAR(255)
- created_at → TIMESTAMP
#### Relationship
- One company → many warehouses (1:N).
##
### Warehouses
```
CREATE TABLE Warehouses (
    warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    FOREIGN KEY (company_id) REFERENCES Companies(company_id)
);
```
#### Attributes
- warehouse_id → INT, PK
- company_id → INT, FK
- name → VARCHAR(255)
- location → VARCHAR(255)
#### Relationship
- One company → many warehouses.
- One warehouse → many inventory records.
##
### Products
```
CREATE TABLE Products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) NOT NULL UNIQUE,
    price DECIMAL(10,2) NOT NULL,
    low_stock_threshold INT DEFAULT 10
);
```
#### Attributes
- product_id → INT, PK
- name → VARCHAR(255)
- sku → VARCHAR(100), UNIQUE
- price → DECIMAL(10,2)
- low_stock_threshold → INT
#### Relationship
- One product → many inventory records.
- One product → many suppliers.
- One product → can be in bundles.
##
### Inventory
```
CREATE TABLE Inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 0),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Products(product_id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouses(warehouse_id),
    UNIQUE (product_id, warehouse_id)
);
```
#### Attributes
- inventory_id → INT, PK
- product_id → INT, FK
- warehouse_id → INT, FK
- quantity → INT
- updated_at → TIMESTAMP
- (product_id, warehouse_id) → UNIQUE
#### Relationship
- Junction table linking Products and Warehouses (many-to-many).
- One inventory → many logs.
##
### Suppliers
```
CREATE TABLE Suppliers (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL
);
```
#### Attributes
- supplier_id → INT, PK
- name → VARCHAR(255)
- contact_email → VARCHAR(255)
#### Relationship
- One supplier → many products (via Product_Suppliers).
##
### Product_Suppliers
```
CREATE TABLE Product_Suppliers (
    product_supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    supplier_id INT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES Products(product_id),
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(supplier_id),
    UNIQUE (product_id, supplier_id)
);
```
#### Attributes
- product_supplier_id → INT, PK
- product_id → INT, FK
- supplier_id → INT, FK
- (product_id, supplier_id) → UNIQUE
#### Relationship
- Junction table for many-to-many between Products and Suppliers.
##
### Inventory_Logs
```
CREATE TABLE Inventory_Logs (
    inventory_log_id INT AUTO_INCREMENT PRIMARY KEY,
    inventory_id INT NOT NULL,
    change INT NOT NULL,
    reason TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inventory_id) REFERENCES Inventory(inventory_id)
);
```
#### Attributes
- inventory_log_id → INT, PK
- inventory_id → INT, FK
- change → INT
- reason → TEXT
- changed_at → TIMESTAMP
#### Relationship
- One inventory → many logs (1:N).
##
### Bundles
```
CREATE TABLE Bundles (
    bundle_id INT AUTO_INCREMENT PRIMARY KEY,
    bundle_product_id INT NOT NULL,
    component_product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (bundle_product_id) REFERENCES Products(product_id),
    FOREIGN KEY (component_product_id) REFERENCES Products(product_id),
    UNIQUE (bundle_product_id, component_product_id)
);
```
#### Attributes
- bundle_id → INT, PK
- bundle_product_id → INT, FK
- component_product_id → INT, FK
- quantity → INT
- (bundle_product_id, component_product_id) → UNIQUE
#### Relationship
- Self-referencing many-to-many relationship on Products.
- One bundle → multiple component products.
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




