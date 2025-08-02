from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal
import os

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    low_stock_threshold = db.Column(db.Integer, default=10)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    updated_at = db.Column(db.DateTime, server_default=db.func.now())

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json

    # Validate required fields
    required = ['name', 'sku', 'price', 'warehouse_id']
    for field in required:
        if field not in data:
            return {"error": f"Missing field: {field}"}, 400

    try:
        # Unique SKU check
        existing = Product.query.filter_by(sku=data['sku']).first()
        if existing:
            return {"error": "SKU must be unique"}, 400

        product = Product(
            name=data['name'],
            sku=data['sku'],
            price=Decimal(str(data['price']))
        )

        db.session.add(product)
        db.session.flush()  # get product.id

        inventory = Inventory(
            product_id=product.id,
            warehouse_id=data['warehouse_id'],
            quantity=data.get('initial_quantity', 0)
        )
        db.session.add(inventory)
        db.session.commit()

        return {"message": "Product created", "product_id": product.id}, 201

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products for testing purposes"""
    products = Product.query.all()
    result = []
    for product in products:
        inventory = Inventory.query.filter_by(product_id=product.id).first()
        result.append({
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "price": float(product.price),
            "warehouse_id": inventory.warehouse_id if inventory else None,
            "quantity": inventory.quantity if inventory else 0
        })
    return {"products": result}

@app.route('/api/test/reset', methods=['POST'])
def reset_database():
    """Reset database for testing purposes"""
    try:
        db.drop_all()
        db.create_all()
        return {"message": "Database reset successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)