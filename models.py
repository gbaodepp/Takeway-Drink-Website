from datetime import datetime
from database import db


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    icon = db.Column(db.String(50), default='☕')
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image_url = db.Column(db.String(300))
    is_available = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(30), nullable=False)
    customer_email = db.Column(db.String(120))
    notes = db.Column(db.Text)
    pickup_time = db.Column(db.String(50))
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending/preparing/ready/completed/cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    @property
    def status_badge(self):
        badges = {
            'pending': 'warning',
            'preparing': 'info',
            'ready': 'primary',
            'completed': 'success',
            'cancelled': 'danger'
        }
        return badges.get(self.status, 'secondary')

    @property
    def status_icon(self):
        icons = {
            'pending': '⏳',
            'preparing': '🔥',
            'ready': '✅',
            'completed': '🎉',
            'cancelled': '❌'
        }
        return icons.get(self.status, '❓')

    def __repr__(self):
        return f'<Order #{self.id}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    qty = db.Column(db.Integer, nullable=False, default=1)

    @property
    def subtotal(self):
        return self.price * self.qty

    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.qty}>'


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'
