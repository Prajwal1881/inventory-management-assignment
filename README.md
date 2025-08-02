# StockFlow - B2B Inventory Management System

## Assignment: Code Review & Debugging

This repository contains the solution for the "Inventory Management System for B2B SaaS" assignment, specifically focusing on **Part 1: Code Review & Debugging**.

## 🔍 Issues Identified in Original Code

### 1. **No Input Validation**
- **Problem**: Missing validation for required fields, data types, and business rules
- **Impact**: Invalid data could corrupt the database and break business logic
- **Fix**: Added comprehensive validation for all input fields with proper error messages

### 2. **No Error Handling**
- **Problem**: No try-catch blocks for database operations
- **Impact**: Unhandled exceptions could crash the application and provide no feedback
- **Fix**: Added proper exception handling with specific error codes and rollback mechanisms

### 3. **Database Transaction Issues**
- **Problem**: Two separate commits instead of one atomic transaction
- **Impact**: If second commit fails, database is left in inconsistent state
- **Fix**: Combined operations into single atomic transaction with proper rollback

### 4. **Missing Business Logic Validation**
- **Problem**: No SKU uniqueness check, warehouse existence validation, or price validation
- **Impact**: Duplicate SKUs, invalid warehouses, and negative prices could break inventory tracking
- **Fix**: Added comprehensive business rule validation

### 5. **Security Issues**
- **Problem**: No input sanitization, direct JSON access without validation
- **Impact**: Potential for injection attacks and data corruption
- **Fix**: Added input sanitization, validation, and proper error handling

### 6. **Poor Error Responses**
- **Problem**: No proper HTTP status codes or detailed error messages
- **Impact**: Difficult debugging and poor API user experience
- **Fix**: Added proper HTTP status codes and structured error responses with codes

## 🚀 Running the Solution

### Prerequisites
```bash
# Install Python 3.8+
python3 --version

# Install dependencies
pip install -r requirements.txt
```

### Start the Application
```bash
# Run the Flask application
python app.py
```

The API will be available at `http://localhost:5000`

### Test the API
```bash
# Run comprehensive tests
python test_api.py
```

## 📚 API Endpoints

### Create Product
```http
POST /api/products
Content-Type: application/json

{
    "name": "Product Name",
    "sku": "PROD-001",
    "price": "99.99",
    "warehouse_id": 1,
    "initial_quantity": 50,
    "description": "Optional description"
}
```

### Get All Products
```http
GET /api/products
```

### Create Warehouse
```http
POST /api/warehouses
Content-Type: application/json

{
    "name": "Warehouse Name",
    "location": "Location"
}
```

### Get All Warehouses
```http
GET /api/warehouses
```

## 🧪 Test Coverage

The test script (`test_api.py`) covers:

1. ✅ Valid product creation
2. ✅ Duplicate SKU prevention
3. ✅ Missing required fields validation
4. ✅ Invalid price rejection
5. ✅ Invalid warehouse validation
6. ✅ Invalid SKU format rejection
7. ✅ Invalid content type handling
8. ✅ Multiple product management
9. ✅ Data retrieval functionality

## 🔧 Key Improvements

### 1. Comprehensive Input Validation
```python
# SKU validation with proper format checking
def validate_sku(sku):
    if not re.match(r'^[A-Z0-9\-_]+$', sku.strip().upper()):
        return False, "SKU can only contain letters, numbers, hyphens, and underscores"
    return True, sku.strip().upper()

# Price validation with decimal handling
def validate_price(price):
    price_decimal = Decimal(str(price))
    if price_decimal < 0:
        return False, "Price must be positive"
    return True, price_decimal
```

### 2. Atomic Database Transactions
```python
try:
    # All database operations in single transaction
    product = Product(name=name, sku=sku, price=price)
    db.session.add(product)
    db.session.flush()  # Get ID without committing
    
    inventory = Inventory(product_id=product.id, warehouse_id=warehouse_id, quantity=initial_quantity)
    db.session.add(inventory)
    
    db.session.commit()  # Single commit for both operations
except SQLAlchemyError:
    db.session.rollback()  # Rollback on any error
```

### 3. Proper Error Handling
```python
# Structured error responses with codes
return jsonify({
    "error": "Product with SKU 'ABC-123' already exists",
    "code": "DUPLICATE_SKU",
    "existing_product_id": existing_product.id
}), 409
```

### 4. Business Logic Enforcement
- SKU uniqueness across platform
- Warehouse existence validation
- Positive price enforcement
- Proper data type validation
- Foreign key constraint handling

## 📊 Database Schema

### Products Table
- `id`: Primary key
- `name`: Product name (required, max 200 chars)
- `sku`: Unique identifier (required, max 50 chars, alphanumeric)
- `price`: Decimal price (required, positive)
- `description`: Optional text description
- `is_active`: Boolean flag for soft deletion
- `created_at`, `updated_at`: Timestamps

### Inventory Table
- `id`: Primary key
- `product_id`: Foreign key to products
- `warehouse_id`: Foreign key to warehouses
- `quantity`: Current stock level
- `reserved_quantity`: Reserved for orders
- `reorder_level`: Minimum stock threshold
- `last_updated`: Timestamp
- **Unique constraint**: `(product_id, warehouse_id)`

### Warehouses Table
- `id`: Primary key
- `name`: Warehouse name (required)
- `location`: Physical location
- `is_active`: Boolean flag
- `created_at`: Timestamp

## 🎯 Production Readiness Features

1. **Logging**: Comprehensive error logging for debugging
2. **Validation**: Input sanitization and business rule enforcement
3. **Transactions**: Atomic operations with proper rollback
4. **Error Codes**: Structured error responses for API consumers
5. **Data Integrity**: Foreign key constraints and unique constraints
6. **Scalability**: Proper indexing on frequently queried fields
7. **Soft Deletion**: `is_active` flags instead of hard deletes

## 🔜 Next Steps (Parts 2 & 3)

This solution provides a solid foundation for:
- **Part 2**: Advanced inventory operations (stock movements, reorder points)
- **Part 3**: Reporting and analytics features

The improved error handling, validation, and database design will support more complex inventory management features while maintaining data integrity and system reliability.

---

**Author**: [Your Name]  
**Assignment**: B2B SaaS Inventory Management System - Part 1  
**Date**: [Current Date]