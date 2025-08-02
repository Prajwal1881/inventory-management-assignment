from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from decimal import Decimal, InvalidOperation
import re
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    reserved_quantity = db.Column(db.Integer, default=0, nullable=False)
    reorder_level = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique combination of product and warehouse
    __table_args__ = (db.UniqueConstraint('product_id', 'warehouse_id', name='_product_warehouse_uc'),)
    
    # Relationships
    product = db.relationship('Product', backref='inventory_records')
    warehouse = db.relationship('Warehouse', backref='inventory_records')

# Validation functions
def validate_sku(sku):
    """Validate SKU format - alphanumeric, hyphens, underscores only"""
    if not sku or len(sku.strip()) == 0:
        return False, "SKU is required"
    
    sku = sku.strip().upper()
    if len(sku) > 50:
        return False, "SKU must be 50 characters or less"
    
    if not re.match(r'^[A-Z0-9\-_]+$', sku):
        return False, "SKU can only contain letters, numbers, hyphens, and underscores"
    
    return True, sku

def validate_price(price):
    """Validate price is a positive decimal"""
    try:
        if isinstance(price, str):
            price_decimal = Decimal(price)
        else:
            price_decimal = Decimal(str(price))
        
        if price_decimal < 0:
            return False, "Price must be positive"
        
        if price_decimal > Decimal('999999.99'):
            return False, "Price too large"
            
        return True, price_decimal
    except (InvalidOperation, ValueError, TypeError):
        return False, "Invalid price format"

def validate_quantity(quantity):
    """Validate quantity is a non-negative integer"""
    try:
        qty = int(quantity)
        if qty < 0:
            return False, "Quantity cannot be negative"
        return True, qty
    except (ValueError, TypeError):
        return False, "Quantity must be a valid integer"

# API Routes
@app.route('/api/products', methods=['POST'])
def create_product():
    """
    Create a new product with initial inventory.
    Improved version with proper validation and error handling.
    """
    try:
        # Validate request has JSON data
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json",
                "code": "INVALID_CONTENT_TYPE"
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Request body must contain valid JSON",
                "code": "EMPTY_REQUEST_BODY"
            }), 400
        
        # Required field validation
        required_fields = ['name', 'sku', 'price', 'warehouse_id']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "code": "MISSING_REQUIRED_FIELDS",
                "missing_fields": missing_fields
            }), 400
        
        # Validate and sanitize inputs
        name = data['name'].strip()
        if len(name) == 0 or len(name) > 200:
            return jsonify({
                "error": "Product name must be between 1 and 200 characters",
                "code": "INVALID_NAME"
            }), 400
        
        # Validate SKU
        sku_valid, sku_result = validate_sku(data['sku'])
        if not sku_valid:
            return jsonify({
                "error": sku_result,
                "code": "INVALID_SKU"
            }), 400
        sku = sku_result
        
        # Validate price
        price_valid, price_result = validate_price(data['price'])
        if not price_valid:
            return jsonify({
                "error": price_result,
                "code": "INVALID_PRICE"
            }), 400
        price = price_result
        
        # Validate warehouse_id
        try:
            warehouse_id = int(data['warehouse_id'])
        except (ValueError, TypeError):
            return jsonify({
                "error": "Warehouse ID must be a valid integer",
                "code": "INVALID_WAREHOUSE_ID"
            }), 400
        
        # Validate initial_quantity if provided
        initial_quantity = 0  # Default value
        if 'initial_quantity' in data:
            qty_valid, qty_result = validate_quantity(data['initial_quantity'])
            if not qty_valid:
                return jsonify({
                    "error": qty_result,
                    "code": "INVALID_QUANTITY"
                }), 400
            initial_quantity = qty_result
        
        # Optional description
        description = data.get('description', '').strip() if data.get('description') else None
        if description and len(description) > 1000:
            return jsonify({
                "error": "Description must be 1000 characters or less",
                "code": "DESCRIPTION_TOO_LONG"
            }), 400
        
        # Start database transaction
        try:
            # Check if warehouse exists and is active
            warehouse = db.session.query(Warehouse).filter_by(
                id=warehouse_id, 
                is_active=True
            ).first()
            
            if not warehouse:
                return jsonify({
                    "error": f"Warehouse with ID {warehouse_id} not found or inactive",
                    "code": "WAREHOUSE_NOT_FOUND"
                }), 404
            
            # Check if SKU already exists
            existing_product = db.session.query(Product).filter_by(sku=sku).first()
            if existing_product:
                return jsonify({
                    "error": f"Product with SKU '{sku}' already exists",
                    "code": "DUPLICATE_SKU",
                    "existing_product_id": existing_product.id
                }), 409
            
            # Create new product
            product = Product(
                name=name,
                sku=sku,
                price=price,
                description=description
            )
            db.session.add(product)
            db.session.flush()  # Get the product ID without committing
            
            # Create inventory record
            inventory = Inventory(
                product_id=product.id,
                warehouse_id=warehouse_id,
                quantity=initial_quantity
            )
            db.session.add(inventory)
            
            # Commit both operations atomically
            db.session.commit()
            
            return jsonify({
                "message": "Product created successfully",
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "sku": product.sku,
                    "price": float(product.price),
                    "description": product.description,
                    "created_at": product.created_at.isoformat()
                },
                "inventory": {
                    "warehouse_id": warehouse_id,
                    "warehouse_name": warehouse.name,
                    "initial_quantity": initial_quantity
                }
            }), 201
            
        except IntegrityError as e:
            db.session.rollback()
            # Handle potential race condition with SKU uniqueness
            if 'sku' in str(e.orig).lower():
                return jsonify({
                    "error": f"Product with SKU '{sku}' already exists",
                    "code": "DUPLICATE_SKU"
                }), 409
            else:
                app.logger.error(f"Database integrity error: {str(e)}")
                return jsonify({
                    "error": "Database constraint violation",
                    "code": "DATABASE_INTEGRITY_ERROR"
                }), 500
        
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Database error in create_product: {str(e)}")
            return jsonify({
                "error": "Database operation failed",
                "code": "DATABASE_ERROR"
            }), 500
    
    except Exception as e:
        app.logger.error(f"Unexpected error in create_product: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "code": "INTERNAL_ERROR"
        }), 500

# Additional helper endpoints for testing
@app.route('/api/warehouses', methods=['POST'])
def create_warehouse():
    """Create a new warehouse for testing purposes"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"error": "Warehouse name is required"}), 400
        
        warehouse = Warehouse(
            name=data['name'],
            location=data.get('location', '')
        )
        db.session.add(warehouse)
        db.session.commit()
        
        return jsonify({
            "message": "Warehouse created",
            "warehouse": {
                "id": warehouse.id,
                "name": warehouse.name,
                "location": warehouse.location
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/warehouses', methods=['GET'])
def get_warehouses():
    """Get all active warehouses"""
    warehouses = Warehouse.query.filter_by(is_active=True).all()
    return jsonify({
        "warehouses": [{
            "id": w.id,
            "name": w.name,
            "location": w.location
        } for w in warehouses]
    })

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with their inventory"""
    products = db.session.query(Product).filter_by(is_active=True).all()
    result = []
    
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "price": float(product.price),
            "description": product.description,
            "inventory": []
        }
        
        for inv in product.inventory_records:
            product_data["inventory"].append({
                "warehouse_id": inv.warehouse_id,
                "warehouse_name": inv.warehouse.name,
                "quantity": inv.quantity,
                "reserved_quantity": inv.reserved_quantity
            })
        
        result.append(product_data)
    
    return jsonify({"products": result})

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()
    
    # Create a default warehouse if none exists
    if not Warehouse.query.first():
        default_warehouse = Warehouse(name="Main Warehouse", location="Default Location")
        db.session.add(default_warehouse)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create a default warehouse for testing
        if not Warehouse.query.first():
            default_warehouse = Warehouse(name="Main Warehouse", location="Default Location")
            db.session.add(default_warehouse)
            db.session.commit()
            print("Created default warehouse")
    
    app.run(debug=True)