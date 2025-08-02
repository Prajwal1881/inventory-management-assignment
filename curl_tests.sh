#!/bin/bash

echo "🧪 Testing Part 1 API with curl commands"
echo "=========================================="

BASE_URL="http://localhost:5000"

echo -e "\n1️⃣ Reset database"
curl -X POST $BASE_URL/api/test/reset
echo -e "\n"

echo "2️⃣ Create a valid product"
curl -X POST $BASE_URL/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "sku": "LAPTOP001",
    "price": 999.99,
    "warehouse_id": 1,
    "initial_quantity": 50
  }'
echo -e "\n"

echo "3️⃣ Try to create duplicate SKU (should fail)"
curl -X POST $BASE_URL/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Another Laptop",
    "sku": "LAPTOP001",
    "price": 899.99,
    "warehouse_id": 1
  }'
echo -e "\n"

echo "4️⃣ Try to create product with missing fields (should fail)"
curl -X POST $BASE_URL/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Incomplete Product",
    "price": 100.00
  }'
echo -e "\n"

echo "5️⃣ Create product without initial_quantity (should work)"
curl -X POST $BASE_URL/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mouse",
    "sku": "MOUSE001",
    "price": 29.99,
    "warehouse_id": 1
  }'
echo -e "\n"

echo "6️⃣ Get all products"
curl -X GET $BASE_URL/api/products
echo -e "\n"

echo "✅ All curl tests completed!"