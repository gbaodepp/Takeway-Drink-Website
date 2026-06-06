# -*- coding: utf-8 -*-
import os
import json
import hashlib
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from database import db, init_db
from models import Product, Category, Order, OrderItem, User

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "baotran110")

# Database config
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'drinks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ── Bootstrap DB (runs for both `python app.py` AND gunicorn) ────────────────
with app.app_context():
    init_db(app)


# ─── Helpers ────────────────────────────────────────────────────────────────

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access that page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_cart():
    return session.get('cart', {})

def save_cart(cart):
    session['cart'] = cart
    session.modified = True

def cart_count():
    return sum(item['qty'] for item in get_cart().values())

def cart_total():
    return sum(item['price'] * item['qty'] for item in get_cart().values())

app.jinja_env.globals.update(cart_count=cart_count, cart_total=cart_total)


# ─── Public Routes ───────────────────────────────────────────────────────────

@app.route('/')
def index():
    categories = Category.query.all()
    featured = Product.query.filter_by(is_available=True, is_featured=True).limit(6).all()
    return render_template('index.html', categories=categories, featured=featured)

@app.route('/menu')
def menu():
    categories = Category.query.all()
    category_id = request.args.get('category', type=int)
    search = request.args.get('q', '').strip()

    query = Product.query.filter_by(is_available=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    products = query.order_by(Product.name).all()
    active_cat = category_id
    return render_template('menu.html', products=products, categories=categories,
                           active_cat=active_cat, search=search)

@app.route('/product/<int:pid>')
def product_detail(pid):
    product = Product.query.get_or_404(pid)
    related = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != pid,
        Product.is_available == True
    ).limit(4).all()
    return render_template('product_detail.html', product=product, related=related)


# ─── Cart Routes ─────────────────────────────────────────────────────────────

@app.route('/cart')
def cart():
    cart = get_cart()
    return render_template('cart.html', cart=cart)

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    pid = str(request.form.get('product_id'))
    qty = int(request.form.get('qty', 1))
    product = Product.query.get_or_404(int(pid))

    cart = get_cart()
    if pid in cart:
        cart[pid]['qty'] += qty
    else:
        cart[pid] = {
            'name': product.name,
            'price': float(product.price),
            'qty': qty,
            'image': product.image_url or ''
        }
    save_cart(cart)
    flash(f'"{product.name}" added to cart!', 'success')
    return redirect(request.referrer or url_for('menu'))

@app.route('/cart/update', methods=['POST'])
def update_cart():
    pid = str(request.form.get('product_id'))
    qty = int(request.form.get('qty', 1))
    cart = get_cart()
    if pid in cart:
        if qty <= 0:
            del cart[pid]
        else:
            cart[pid]['qty'] = qty
    save_cart(cart)
    return redirect(url_for('cart'))

@app.route('/cart/remove/<pid>')
def remove_from_cart(pid):
    cart = get_cart()
    cart.pop(pid, None)
    save_cart(cart)
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))

@app.route('/cart/clear')
def clear_cart():
    save_cart({})
    return redirect(url_for('cart'))


# ─── Checkout ────────────────────────────────────────────────────────────────

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = get_cart()
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('menu'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        notes = request.form.get('notes', '').strip()
        pickup_time = request.form.get('pickup_time', '').strip()

        if not name or not phone:
            flash('Name and phone number are required.', 'danger')
            return render_template('checkout.html', cart=cart)

        total = cart_total()
        order = Order(
            customer_name=name,
            customer_phone=phone,
            customer_email=email,
            notes=notes,
            pickup_time=pickup_time,
            total_price=total,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()

        for pid, item in cart.items():
            oi = OrderItem(
                order_id=order.id,
                product_id=int(pid),
                product_name=item['name'],
                price=item['price'],
                qty=item['qty']
            )
            db.session.add(oi)

        db.session.commit()
        save_cart({})
        flash(f'Order #{order.id} placed successfully! 🎉', 'success')
        return redirect(url_for('order_confirmation', oid=order.id))

    return render_template('checkout.html', cart=cart)

@app.route('/order/confirmation/<int:oid>')
def order_confirmation(oid):
    order = Order.query.get_or_404(oid)
    return render_template('order_confirmation.html', order=order)

@app.route('/order/track', methods=['GET', 'POST'])
def track_order():
    order = None
    if request.method == 'POST':
        oid = request.form.get('order_id', '').strip()
        phone = request.form.get('phone', '').strip()
        if oid and phone:
            order = Order.query.filter_by(id=int(oid), customer_phone=phone).first()
            if not order:
                flash('No order found with that ID and phone number.', 'danger')
    return render_template('track_order.html', order=order)


# ─── Auth ─────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and user.password_hash == hash_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('admin_dashboard') if user.is_admin else url_for('index'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ─── Admin Routes ─────────────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_orders = Order.query.count()
    pending = Order.query.filter_by(status='pending').count()
    preparing = Order.query.filter_by(status='preparing').count()
    completed = Order.query.filter_by(status='completed').count()
    revenue = db.session.query(db.func.sum(Order.total_price)).filter(
        Order.status == 'completed').scalar() or 0
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    products_count = Product.query.count()
    return render_template('admin/dashboard.html',
                           total_orders=total_orders, pending=pending,
                           preparing=preparing, completed=completed,
                           revenue=revenue, recent_orders=recent_orders,
                           products_count=products_count)

@app.route('/admin/orders')
@admin_required
def admin_orders():
    status_filter = request.args.get('status', '')
    query = Order.query.order_by(Order.created_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter)
    orders = query.all()
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

@app.route('/admin/order/<int:oid>')
@admin_required
def admin_order_detail(oid):
    order = Order.query.get_or_404(oid)
    return render_template('admin/order_detail.html', order=order)

@app.route('/admin/order/<int:oid>/status', methods=['POST'])
@admin_required
def update_order_status(oid):
    order = Order.query.get_or_404(oid)
    new_status = request.form.get('status')
    if new_status in ['pending', 'preparing', 'ready', 'completed', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{oid} status updated to "{new_status}".', 'success')
    return redirect(request.referrer or url_for('admin_orders'))

@app.route('/admin/products')
@admin_required
def admin_products():
    products = Product.query.order_by(Product.category_id, Product.name).all()
    categories = Category.query.all()
    return render_template('admin/products.html', products=products, categories=categories)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    categories = Category.query.all()
    if request.method == 'POST':
        p = Product(
            name=request.form['name'],
            description=request.form.get('description', ''),
            price=float(request.form['price']),
            category_id=int(request.form['category_id']),
            image_url=request.form.get('image_url', ''),
            is_available=bool(request.form.get('is_available')),
            is_featured=bool(request.form.get('is_featured'))
        )
        db.session.add(p)
        db.session.commit()
        flash(f'Product "{p.name}" added.', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', product=None, categories=categories)

@app.route('/admin/product/edit/<int:pid>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(pid):
    product = Product.query.get_or_404(pid)
    categories = Category.query.all()
    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form.get('description', '')
        product.price = float(request.form['price'])
        product.category_id = int(request.form['category_id'])
        product.image_url = request.form.get('image_url', '')
        product.is_available = bool(request.form.get('is_available'))
        product.is_featured = bool(request.form.get('is_featured'))
        db.session.commit()
        flash(f'Product "{product.name}" updated.', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html', product=product, categories=categories)

@app.route('/admin/product/delete/<int:pid>', methods=['POST'])
@admin_required
def admin_delete_product(pid):
    product = Product.query.get_or_404(pid)
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{product.name}" deleted.', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/product/toggle/<int:pid>', methods=['POST'])
@admin_required
def toggle_product(pid):
    product = Product.query.get_or_404(pid)
    product.is_available = not product.is_available
    db.session.commit()
    return redirect(request.referrer or url_for('admin_products'))


# ─── API (AJAX) ───────────────────────────────────────────────────────────────

@app.route('/api/cart/count')
def api_cart_count():
    return jsonify({'count': cart_count(), 'total': cart_total()})


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=5000)
