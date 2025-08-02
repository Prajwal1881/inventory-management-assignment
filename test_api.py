"""
Test script for StockFlow API - demonstrates corrected functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_get_warehouses():
    """Test getting warehouses"""
    print("🏭 Testing get warehouses...")
    response = requests.get(f"{BASE_URL}/warehouses")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {data['total']} warehouses")
    for warehouse in data['warehouses']:
        print(f"  - {warehouse['name']} ({warehouse['location']})")
    print()
    return data['warehouses']

def test_create_product_success(warehouse_id):
    """Test successful product creation"""
    print("✅ Testing successful product creation...")
    
    product_data = {
        "name": "MacBook Pro 16-inch",
        "sku": "APPLE-MBP-16-2023",
        "price": 2499.99,
        "description": "Latest MacBook Pro with M3 chip",
        "warehouse_id": warehouse_id,
        "initial_quantity": 10
    }
    
    response = requests.post(
        f"{BASE_URL}/products",
        json=product_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    return response.json() if response.status_code == 201 else None

def test_create_product_validation_errors():
    """Test validation error scenarios"""
    print("❌ Testing validation errors...")
    
    # Test missing required fields
    invalid_data = {
        "name": "Invalid Product"
        # Missing required fields
    }
    
    response = requests.post(
        f"{BASE_URL}/products",
        json=invalid_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Missing fields - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test invalid price
    invalid_price_data = {
        "name": "Invalid Price Product",
        "sku": "INVALID-PRICE",
        "price": -10.0,  # Negative price
        "warehouse_id": "some-id",
        "initial_quantity": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/products",
        json=invalid_price_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Invalid price - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_create_product_duplicate_sku(warehouse_id):
    """Test duplicate SKU error"""
    print("🔄 Testing duplicate SKU error...")
    
    product_data = {
        "name": "Duplicate SKU Product",
        "sku": "APPLE-MBP-16-2023",  # Same SKU as before
        "price": 1999.99,
        "warehouse_id": warehouse_id,
        "initial_quantity": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/products",
        json=product_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_create_product_invalid_warehouse():
    """Test invalid warehouse ID error"""
    print("🏭❌ Testing invalid warehouse ID...")
    
    product_data = {
        "name": "Product with Invalid Warehouse",
        "sku": "INVALID-WAREHOUSE-TEST",
        "price": 99.99,
        "warehouse_id": "non-existent-warehouse-id",
        "initial_quantity": 5
    }
    
    response = requests.post(
        f"{BASE_URL}/products",
        json=product_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_get_products():
    """Test getting all products"""
    print("📦 Testing get products...")
    response = requests.get(f"{BASE_URL}/products")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {data['total']} products")
    for product in data['products']:
        print(f"  - {product['name']} (SKU: {product['sku']}) - ${product['price']}")
        for inventory in product['inventories']:
            print(f"    Warehouse: {inventory['warehouse_name']} - Qty: {inventory['quantity']}")
    print()

def test_content_type_error():
    """Test content type validation"""
    print("🔍 Testing content type validation...")
    
    # Send data without proper content type
    response = requests.post(
        f"{BASE_URL}/products",
        data="invalid data",  # Not JSON
        headers={'Content-Type': 'text/plain'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def main():
    """Run all tests"""
    print("🚀 Starting StockFlow API Tests")
    print("=" * 50)
    
    try:
        # Test health check
        test_health_check()
        
        # Get warehouses first
        warehouses = test_get_warehouses()
        if not warehouses:
            print("❌ No warehouses found! Cannot continue tests.")
            return
        
        warehouse_id = warehouses[0]['id']
        
        # Test successful product creation
        product = test_create_product_success(warehouse_id)
        
        # Test validation errors
        test_create_product_validation_errors()
        
        # Test duplicate SKU
        if product:
            test_create_product_duplicate_sku(warehouse_id)
        
        # Test invalid warehouse
        test_create_product_invalid_warehouse()
        
        # Test content type error
        test_content_type_error()
        
        # Get all products
        test_get_products()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the Flask app is running on localhost:5000")
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    main()