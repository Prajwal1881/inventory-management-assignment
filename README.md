# StockFlow - Inventory Management System Assignment

This project demonstrates the solution for **Part 1: Code Review & Debugging** of the StockFlow B2B inventory management system assignment.

## Overview

StockFlow is a B2B inventory management platform that helps small businesses track products across multiple warehouses and manage supplier relationships.

## Assignment Solution

### Part 1: Code Review & Debugging

The original API endpoint had several critical issues that have been identified and fixed. See [`part1_analysis.md`](part1_analysis.md) for detailed analysis.

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Test the API:**
   ```bash
   python test_api.py
   ```

The application will be available at `http://localhost:5000`

## API Endpoints

### Products

#### Create Product
```http
POST /api/products
Content-Type: application/json

{
    "name": "MacBook Pro 16-inch",
    "sku": "APPLE-MBP-16-2023",
    "price": 2499.99,
    "description": "Latest MacBook Pro with M3 chip",
    "warehouse_id": "warehouse-uuid",
    "initial_quantity": 10
}
```

#### Get All Products
```http
GET /api/products
```

### Warehouses

#### Create Warehouse
```http
POST /api/warehouses
Content-Type: application/json

{
    "name": "Main Warehouse",
    "location": "New York, NY"
}
```

#### Get All Warehouses
```http
GET /api/warehouses
```

### Health Check
```http
GET /api/health
```

## Key Issues Fixed

### 1. **Database Design Problems**
- ❌ **Original**: Products had `warehouse_id` field, violating "products can exist in multiple warehouses" rule
- ✅ **Fixed**: Removed `warehouse_id` from Product model, products are now warehouse-agnostic

### 2. **Input Validation Issues**
- ❌ **Original**: No validation, direct dictionary access causing KeyError exceptions
- ✅ **Fixed**: Comprehensive input validation using Marshmallow schemas

### 3. **Error Handling Deficiencies**
- ❌ **Original**: No exception handling, no rollback mechanism
- ✅ **Fixed**: Proper exception handling with transaction rollbacks and appropriate HTTP status codes

### 4. **Business Logic Violations**
- ❌ **Original**: SKU uniqueness not enforced, invalid warehouse IDs accepted
- ✅ **Fixed**: SKU uniqueness validation, warehouse existence checks

### 5. **Transaction Management**
- ❌ **Original**: Two separate database commits, risk of partial failures
- ✅ **Fixed**: Single transaction with proper rollback on failures

## Database Schema

### Product Model
```python
class Product(db.Model):
    id = String(36) [Primary Key]
    name = String(255) [Required]
    sku = String(100) [Unique, Required, Indexed]
    price = Numeric(10,2) [Required]
    description = Text [Optional]
    created_at = DateTime
    updated_at = DateTime
```

### Warehouse Model
```python
class Warehouse(db.Model):
    id = String(36) [Primary Key]
    name = String(255) [Required]
    location = String(255) [Required]
    created_at = DateTime
```

### Inventory Model
```python
class Inventory(db.Model):
    id = String(36) [Primary Key]
    product_id = String(36) [Foreign Key to Product]
    warehouse_id = String(36) [Foreign Key to Warehouse]
    quantity = Integer [Required, Default: 0]
    reserved_quantity = Integer [Required, Default: 0]
    created_at = DateTime
    updated_at = DateTime
    
    # Unique constraint on (product_id, warehouse_id)
```

## Testing

The `test_api.py` script demonstrates all the fixed functionality:

- ✅ Successful product creation
- ✅ Input validation error handling
- ✅ Duplicate SKU detection
- ✅ Invalid warehouse ID handling
- ✅ Content-type validation
- ✅ Proper HTTP status codes

Run tests with:
```bash
python test_api.py
```

## Production Improvements

### Security
- Input sanitization via schema validation
- Safe error messages (no sensitive data exposure)
- Proper content-type checking

### Data Integrity
- Database constraints for SKU uniqueness
- Foreign key constraints
- Transaction consistency

### Monitoring & Debugging
- Comprehensive logging
- Audit trails with timestamps
- Proper error categorization

### Performance
- Database indexes on SKU and foreign keys
- Efficient queries with proper relationships
- UUID primary keys for better scalability

## File Structure

```
.
├── app.py                 # Main Flask application
├── part1_analysis.md      # Detailed code review analysis
├── test_api.py           # API testing script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Error Response Examples

### Validation Error (400)
```json
{
    "error": "Validation failed",
    "details": {
        "sku": ["SKU is required"],
        "price": ["Price must be greater than 0.01"]
    }
}
```

### Warehouse Not Found (404)
```json
{
    "error": "Warehouse not found",
    "warehouse_id": "invalid-warehouse-id"
}
```

### Duplicate SKU (409)
```json
{
    "error": "SKU already exists",
    "sku": "EXISTING-SKU"
}
```

### Server Error (500)
```json
{
    "error": "Internal server error"
}
```

## Assignment Requirements Met

✅ **Identified Issues**: All technical and business logic problems documented  
✅ **Explained Impact**: Production impact analysis for each issue  
✅ **Provided Fixes**: Complete corrected implementation with explanations  
✅ **Business Rules**: Products can exist in multiple warehouses  
✅ **Unique SKUs**: Platform-wide SKU uniqueness enforced  
✅ **Decimal Prices**: Proper decimal handling for prices  
✅ **Optional Fields**: Flexible schema with optional description field  

## Next Steps

This implementation provides a solid foundation for Parts 2 and 3 of the assignment. The corrected code follows best practices for:

- RESTful API design
- Database modeling
- Error handling
- Input validation
- Security considerations
- Production readiness