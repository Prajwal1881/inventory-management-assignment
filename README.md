# inventory-management-assignment

This repository contains my submission for the Backend Engineering Intern Case Study:  
**Inventory Management System for B2B SaaS**

---

## 📌 Repository Contents
- **PART1_CodeReview.md** → Code review, identified issues, and corrected version.
- **PART2_DatabaseDesign.md** → SQL schema with data types, primary/foreign keys, and relationships.
- **PART3_APIImplementation/** → Flask implementation of the low-stock alerts API.

---

## 🛠️ Technologies Used
- **Backend Framework:** Python (Flask)
- **ORM:** SQLAlchemy
- **Database:** MySQL (assumed)
- **Schema Format:** SQL + Markdown text descriptions

---

## 📂 Parts Overview

### Part 1: Code Review & Debugging
- Reviewed a product creation API endpoint.
- **Issues Identified:** 
  - Missing SKU uniqueness check  
  - Incorrect handling for multiple warehouses  
  - Lack of error handling and transactions  
  - Price stored without decimal precision  
  - Assumption of always having `initial_quantity`  
- **Fixes Applied:**  
  - Added SKU uniqueness validation  
  - Used a single transaction  
  - Default handling for optional fields  
  - Decimal type for price  
  - Warehouse relation moved to Inventory table  

See [`Part1_CodeReview.md`](./Part1_CodeReview.md).

---

### Part 2: Database Design
- Designed a normalized schema for **StockFlow**.
- Tables: **Companies, Warehouses, Products, Inventory, Suppliers, Product_Suppliers, Inventory_Logs, Bundles**
- Each table defined with:
  - SQL `CREATE TABLE` statement  
  - Attributes with data type + PK, FK, Unique  
  - Relationship explanation  

✅ Example:  
**Products**
- `product_id` → INT, PK  
- `name` → VARCHAR(255)  
- `sku` → VARCHAR(100), UNIQUE  
- `price` → DECIMAL(10,2)  
- `low_stock_threshold` → INT  

See [`Part2_DatabaseDesign.md`](./Part2_DatabaseDesign.md).

---

### Part 3: API Implementation
- Implemented endpoint:  
  ```http
  GET /api/companies/{company_id}/alerts/low-stock

#### Business Rules Implemented:
- Products with stock below their threshold trigger alerts
- Supplier details included for reordering
- Supports multiple warehouses per company
- Added placeholder logic for estimating days_until_stockout
#### Edge Cases Handled:
- No products below threshold → returns empty list
- Invalid company_id → returns empty alerts
- Division by zero in stockout calculation avoided
- Products without threshold → default set at 10
- Graceful error handling with try-except

See [`Part3_APIImplementation.md`](./Part3_APIImplementation.md).


### 🔑 Assumptions
- SKUs are globally unique across the platform.
- Price stored as DECIMAL(10,2) for accuracy.
- Default low stock threshold = 10 if not specified.
- Recent sales activity would be checked via Inventory_Logs (placeholder logic in this implementation).
- Each product has at least one supplier.
