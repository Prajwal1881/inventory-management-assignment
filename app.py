"""
StockFlow - B2B Inventory Management System
Part 1: Corrected Implementation
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from marshmallow import Schema, fields, validate, ValidationError, post_load
from decimal import Decimal
import uuid
from datetime import datetime
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import os

# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///stockflow.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    inventories = db.relationship('Inventory', back_populates='product', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'sku': self.sku,
            'price': float(self.price),
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    inventories = db.relationship('Inventory', back_populates='warehouse')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'created_at': self.created_at.isoformat()
        }

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.String(36), db.ForeignKey('warehouses.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    reserved_quantity = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', back_populates='inventories')
    warehouse = db.relationship('Warehouse', back_populates='inventories')
    
    # Unique constraint for product-warehouse combination
    __table_args__ = (
        UniqueConstraint('product_id', 'warehouse_id', name='unique_product_warehouse'),
    )
    
    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'warehouse_id': self.warehouse_id,
            'quantity': self.quantity,
            'reserved_quantity': self.reserved_quantity,
            'available_quantity': self.available_quantity,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Validation Schemas
class CreateProductSchema(Schema):
    name = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=255),
        error_messages={'required': 'Product name is required'}
    )
    sku = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'SKU is required'}
    )
    price = fields.Decimal(
        required=True, 
        places=2,
        validate=validate.Range(min=0.01),
        error_messages={'required': 'Price is required'}
    )
    description = fields.Str(
        missing=None,
        validate=validate.Length(max=1000)
    )
    warehouse_id = fields.Str(
        required=True,
        error_messages={'required': 'Warehouse ID is required'}
    )
    initial_quantity = fields.Int(
        required=True,
        validate=validate.Range(min=0),
        error_messages={'required': 'Initial quantity is required'}
    )
    
    @post_load
    def normalize_sku(self, data, **kwargs):
        # Normalize SKU to uppercase for consistency
        data['sku'] = data['sku'].upper().strip()
        return data

class CreateWarehouseSchema(Schema):
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        error_messages={'required': 'Warehouse name is required'}
    )
    location = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        error_messages={'required': 'Warehouse location is required'}
    )

# API Routes

@app.route('/api/products', methods=['POST'])
def create_product():
    """
    Create a new product with initial inventory in a specific warehouse.
    
    Expected JSON payload:
    {
        "name": "Product Name",
        "sku": "PROD-001",
        "price": 29.99,
        "description": "Optional description",
        "warehouse_id": "warehouse-uuid",
        "initial_quantity": 100
    }
    """
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        # Get and validate input data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body is required'
            }), 400
        
        # Validate input schema
        schema = CreateProductSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            logger.warning(f"Validation error: {err.messages}")
            return jsonify({
                'error': 'Validation failed',
                'details': err.messages
            }), 400
        
        # Check if warehouse exists
        warehouse = Warehouse.query.get(validated_data['warehouse_id'])
        if not warehouse:
            return jsonify({
                'error': 'Warehouse not found',
                'warehouse_id': validated_data['warehouse_id']
            }), 404
        
        # Start database transaction
        try:
            # Check if SKU already exists
            existing_product = Product.query.filter_by(sku=validated_data['sku']).first()
            if existing_product:
                return jsonify({
                    'error': 'SKU already exists',
                    'sku': validated_data['sku']
                }), 409
            
            # Create new product
            product = Product(
                name=validated_data['name'],
                sku=validated_data['sku'],
                price=validated_data['price'],
                description=validated_data.get('description')
            )
            db.session.add(product)
            db.session.flush()  # Get the product ID without committing
            
            # Create inventory record
            inventory = Inventory(
                product_id=product.id,
                warehouse_id=validated_data['warehouse_id'],
                quantity=validated_data['initial_quantity']
            )
            db.session.add(inventory)
            
            # Commit both operations together
            db.session.commit()
            
            logger.info(f"Product created successfully: {product.id}")
            
            return jsonify({
                'message': 'Product created successfully',
                'product': product.to_dict(),
                'inventory': {
                    'warehouse_id': inventory.warehouse_id,
                    'quantity': inventory.quantity
                }
            }), 201
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Database integrity error: {str(e)}")
            return jsonify({
                'error': 'Database constraint violation',
                'details': 'SKU must be unique or warehouse constraint failed'
            }), 409
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error: {str(e)}")
            return jsonify({
                'error': 'Database operation failed'
            }), 500
            
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Unexpected error in create_product: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@app.route('/api/warehouses', methods=['POST'])
def create_warehouse():
    """Create a new warehouse."""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        schema = CreateWarehouseSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            return jsonify({
                'error': 'Validation failed',
                'details': err.messages
            }), 400
        
        warehouse = Warehouse(
            name=validated_data['name'],
            location=validated_data['location']
        )
        
        db.session.add(warehouse)
        db.session.commit()
        
        logger.info(f"Warehouse created successfully: {warehouse.id}")
        
        return jsonify({
            'message': 'Warehouse created successfully',
            'warehouse': warehouse.to_dict()
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'Database operation failed'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in create_warehouse: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with their inventory information."""
    try:
        products = Product.query.all()
        result = []
        
        for product in products:
            product_data = product.to_dict()
            # Add inventory information
            inventories = []
            for inventory in product.inventories:
                inventories.append({
                    'warehouse_id': inventory.warehouse_id,
                    'warehouse_name': inventory.warehouse.name,
                    'quantity': inventory.quantity,
                    'reserved_quantity': inventory.reserved_quantity,
                    'available_quantity': inventory.available_quantity
                })
            product_data['inventories'] = inventories
            result.append(product_data)
        
        return jsonify({
            'products': result,
            'total': len(result)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving products: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/warehouses', methods=['GET'])
def get_warehouses():
    """Get all warehouses."""
    try:
        warehouses = Warehouse.query.all()
        result = [warehouse.to_dict() for warehouse in warehouses]
        
        return jsonify({
            'warehouses': result,
            'total': len(result)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving warehouses: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# Initialize database
@app.before_first_request
def create_tables():
    """Create database tables."""
    db.create_all()
    
    # Create default warehouses if none exist
    if Warehouse.query.count() == 0:
        default_warehouses = [
            Warehouse(name="Main Warehouse", location="New York, NY"),
            Warehouse(name="West Coast Warehouse", location="Los Angeles, CA"),
            Warehouse(name="East Coast Warehouse", location="Boston, MA")
        ]
        
        for warehouse in default_warehouses:
            db.session.add(warehouse)
        
        db.session.commit()
        logger.info("Created default warehouses")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)