from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and user management"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationship with Cart
    cart_items = db.relationship('Cart', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Category(db.Model):
    """Category model for product categories"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relationship with Products
    products = db.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    """Product model for store items"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)  # Changed from image_url to image_filename
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    # Relationship with Cart
    cart_items = db.relationship('Cart', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def get_image_url(self):
        """Get the URL for the product image"""
        if self.image_filename:
            return f'/static/uploads/{self.image_filename}'
        return '/static/uploads/placeholder.svg'
    
    def __repr__(self):
        return f'<Product {self.name}>'


class Cart(db.Model):
    """Cart model for shopping cart items"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    def __repr__(self):
        return f'<Cart user_id={self.user_id} product_id={self.product_id}>'
    
    def get_subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.product.price * self.quantity


class Order(db.Model):
    """Order model for customer orders"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='COD')
    order_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(50), default='Pending')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Optional: link to user if logged in
    
    # Relationship with OrderItems
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def can_be_cancelled(self):
        """Check if order can be cancelled (within 24 hours and status is Pending)"""
        if self.status != 'Pending':
            return False
        
        # Check if order is within 24 hours
        from datetime import timedelta
        time_elapsed = datetime.now(timezone.utc) - self.order_date
        return time_elapsed < timedelta(hours=24)
    
    def calculate_total(self):
        """Calculate total amount from order items"""
        return sum(item.get_subtotal() for item in self.order_items)
    
    def get_status_badge_class(self):
        """Get Bootstrap badge class for order status"""
        status_classes = {
            'Pending': 'bg-warning text-dark',
            'Processing': 'bg-info',
            'Packed': 'bg-info',
            'Shipped': 'bg-primary',
            'Delivered': 'bg-success',
            'Cancelled': 'bg-danger'
        }
        return status_classes.get(self.status, 'bg-secondary')
    
    def __repr__(self):
        return f'<Order {self.id} - {self.name}>'


class OrderItem(db.Model):
    """OrderItem model for items in an order"""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    def get_subtotal(self):
        """Calculate subtotal for this order item"""
        return self.price * self.quantity
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x {self.quantity}>'
