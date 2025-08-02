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

See [`PART1_CodeReview.md`](./PART1_CodeReview.md).

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

See [`PART2_DatabaseDesign.md`](./PART2_DatabaseDesign.md).

---

### Part 3: API Implementation
- Implemented endpoint:  
  ```http
  GET /api/companies/{company_id}/alerts/low-stock
