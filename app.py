from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models import db, User, Category, Product, Cart, Order, OrderItem
from forms import LoginForm, SignupForm, ProductForm, CategoryForm, CheckoutForm

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration (Gmail SMTP)
# ⚠️ IMPORTANT: Replace 'admin123' with your Gmail App Password (16 characters)
# Generate at: https://myaccount.google.com/apppasswords
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'secretsclanstore@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Will load from .env
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'secretsclanstore@gmail.com')
app.config['ADMIN_EMAIL'] = os.environ.get('ADMIN_EMAIL', 'hi89141na@gmail.com')
app.config['BASE_URL'] = os.environ.get('BASE_URL', 'http://localhost:5000')

# File upload configuration
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize extensions
db.init_app(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Register blueprints
from routes import orders_bp
app.register_blueprint(orders_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper function to check allowed file extensions
def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Helper function to delete image file
def delete_image_file(filename):
    """Delete image file from uploads folder"""
    if filename and filename not in ['placeholder.png', 'placeholder.svg']:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"Error deleting file: {e}")
                return False
    return False


# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ============ PUBLIC ROUTES ============

@app.route('/')
def index():
    """Homepage showing categories and featured products"""
    categories = Category.query.all()
    products = Product.query.limit(6).all()
    return render_template('index.html', categories=categories, products=products)


@app.route('/search')
def search():
    """Search for products by name or category"""
    query = request.args.get('q', '')
    if query:
        # Search in product names and category names
        products = Product.query.join(Category).filter(
            db.or_(
                Product.name.ilike(f'%{query}%'),
                Product.description.ilike(f'%{query}%'),
                Category.name.ilike(f'%{query}%')
            )
        ).all()
    else:
        products = []
    
    return render_template('search.html', query=query, products=products)


@app.route('/category/<string:name>')
def category(name):
    """Display products in a specific category"""
    category = Category.query.filter_by(name=name).first_or_404()
    products = Product.query.filter_by(category_id=category.id).all()
    return render_template('category.html', category=category, products=products)


@app.route('/product/<int:id>')
def product(id):
    """Display product details"""
    product = Product.query.get_or_404(id)
    return render_template('product.html', product=product)


# ============ CART ROUTES ============

@app.route('/cart')
@login_required
def cart():
    """View shopping cart"""
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total = sum(item.get_subtotal() for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add product to cart"""
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    # Check if item already in cart
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('cart'))


@app.route('/cart/update/<int:cart_id>', methods=['POST'])
@login_required
def update_cart(cart_id):
    """Update cart item quantity"""
    cart_item = Cart.query.get_or_404(cart_id)
    
    if cart_item.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('cart'))
    
    quantity = int(request.form.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        db.session.commit()
        flash('Cart updated!', 'success')
    else:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart.', 'success')
    
    return redirect(url_for('cart'))


@app.route('/cart/remove/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    """Remove item from cart"""
    cart_item = Cart.query.get_or_404(cart_id)
    
    if cart_item.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'success')
    return redirect(url_for('cart'))


# ============ CHECKOUT AND ORDER ROUTES ============

# Import email service
from utils.email_service import send_order_confirmation

def send_order_emails(order, user):
    """Send order confirmation emails to admin and customer (wrapper for email_service)"""
    return send_order_confirmation(mail, order, user)


@app.route('/checkout')
@login_required
def checkout():
    """Display checkout page"""
    # Get cart items
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty. Add items before checking out.', 'warning')
        return redirect(url_for('cart'))
    
    # Check if any products have been deleted
    invalid_items = []
    for item in cart_items:
        if not item.product:
            invalid_items.append(item)
    
    # Remove invalid items
    if invalid_items:
        for item in invalid_items:
            db.session.delete(item)
        db.session.commit()
        flash('Some items in your cart were no longer available and have been removed.', 'warning')
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        
        if not cart_items:
            flash('Your cart is now empty.', 'warning')
            return redirect(url_for('cart'))
    
    # Calculate total
    total = sum(item.get_subtotal() for item in cart_items)
    
    # Pre-fill form with user data
    form = CheckoutForm()
    if not form.is_submitted():
        form.name.data = current_user.name
        form.email.data = current_user.email
    
    return render_template('checkout.html', form=form, cart_items=cart_items, total=total)


@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    """Process order and send confirmation emails"""
    form = CheckoutForm()
    
    if form.validate_on_submit():
        # Get cart items
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        
        if not cart_items:
            flash('Your cart is empty.', 'danger')
            return redirect(url_for('cart'))
        
        # Calculate total
        total = sum(item.get_subtotal() for item in cart_items)
        
        # Create order
        order = Order(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            total_price=total,
            payment_method='COD',
            status='Pending',
            user_id=current_user.id
        )
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items
        order_items = []
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            order_items.append(order_item)
            db.session.add(order_item)
        
        # Clear cart
        for cart_item in cart_items:
            db.session.delete(cart_item)
        
        db.session.commit()
        
        # Send emails with user object instead of order_items
        email_sent = send_order_emails(order, current_user)
        
        if email_sent:
            flash('Order placed successfully! Confirmation emails have been sent.', 'success')
        else:
            flash('Order placed successfully! However, there was an issue sending confirmation emails.', 'warning')
        
        # Store order details in session for success page
        session['last_order_id'] = order.id
        session['customer_name'] = order.name
        
        return redirect(url_for('order_success'))
    
    # If form validation fails
    flash('Please fill in all required fields correctly.', 'danger')
    return redirect(url_for('checkout'))


@app.route('/order_success')
@login_required
def order_success():
    """Display order success page"""
    order_id = session.pop('last_order_id', None)
    customer_name = session.pop('customer_name', current_user.name)
    
    if not order_id:
        flash('No recent order found.', 'warning')
        return redirect(url_for('index'))
    
    order = db.session.get(Order, order_id)
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('order_success.html', order=order, customer_name=customer_name)


# User order routes moved to routes/orders.py blueprint

# ============ AUTHENTICATION ROUTES ============

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data,
            is_admin=False
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ============ ADMIN ROUTES ============

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics"""
    total_users = User.query.count()
    total_products = Product.query.count()
    total_categories = Category.query.count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_products=total_products,
                         total_categories=total_categories)


# -------- ADMIN PRODUCTS --------

@app.route('/admin/products')
@admin_required
def admin_products():
    """View all products"""
    products = Product.query.all()
    return render_template('admin/products.html', products=products)


@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    """Add new product"""
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid filename conflicts
                import time
                timestamp = str(int(time.time()))
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
            elif file and file.filename:
                flash('Invalid file type. Only JPG, JPEG, and PNG are allowed.', 'danger')
                return render_template('admin/product_form.html', form=form, action='Add')
        
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image_filename=image_filename,
            category_id=form.category_id.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', form=form, action='Add')


@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(id):
    """Edit existing product"""
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                # Delete old image if exists
                if product.image_filename:
                    delete_image_file(product.image_filename)
                
                # Save new image
                filename = secure_filename(file.filename)
                import time
                timestamp = str(int(time.time()))
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.image_filename = filename
            elif file and file.filename:
                flash('Invalid file type. Only JPG, JPEG, and PNG are allowed.', 'danger')
                return render_template('admin/product_form.html', form=form, action='Edit', product=product)
        
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.category_id = form.category_id.data
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', form=form, action='Edit', product=product)


@app.route('/admin/products/delete/<int:id>')
@admin_required
def admin_delete_product(id):
    """Delete product"""
    product = Product.query.get_or_404(id)
    
    # Delete associated image file
    if product.image_filename:
        delete_image_file(product.image_filename)
    
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin_products'))


# -------- ADMIN CATEGORIES --------

@app.route('/admin/categories')
@admin_required
def admin_categories():
    """View all categories"""
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)


@app.route('/admin/categories/add', methods=['GET', 'POST'])
@admin_required
def admin_add_category():
    """Add new category"""
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_form.html', form=form, action='Add')


@app.route('/admin/categories/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_category(id):
    """Edit existing category"""
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin/category_form.html', form=form, action='Edit')


@app.route('/admin/categories/delete/<int:id>')
@admin_required
def admin_delete_category(id):
    """Delete category"""
    category = Category.query.get_or_404(id)
    
    if category.products:
        flash('Cannot delete category with existing products.', 'danger')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    
    return redirect(url_for('admin_categories'))


# -------- ADMIN USERS --------

@app.route('/admin/users')
@admin_required
def admin_users():
    """View all users"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/delete/<int:id>')
@admin_required
def admin_delete_user(id):
    """Delete user"""
    if id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_users'))


# -------- ADMIN ORDERS --------
# Admin order routes moved to routes/orders.py blueprint


# -------- ADMIN EMAIL TEST --------

@app.route('/admin/test-email')
@admin_required
def admin_test_email():
    """Test email configuration by sending a test email"""
    try:
        from flask_mail import Message
        
        # Log configuration (without password)
        print("\n" + "="*60)
        print("📧 EMAIL CONFIGURATION TEST")
        print("="*60)
        print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
        print(f"MAIL_PASSWORD: {'*' * len(app.config.get('MAIL_PASSWORD', ''))}")
        print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        print(f"ADMIN_EMAIL: {app.config.get('ADMIN_EMAIL')}")
        print("="*60)
        
        # Create test message
        msg = Message(
            subject='🧪 SecretsClan Email Test - Configuration Successful',
            sender=app.config.get('MAIL_DEFAULT_SENDER'),
            recipients=[app.config.get('ADMIN_EMAIL')]
        )
        
        msg.body = f"""
🎉 SUCCESS! Email Configuration is Working!

This is a test email from SecretsClan Order Management System.

CONFIGURATION DETAILS:
---------------------
Mail Server: {app.config.get('MAIL_SERVER')}
Mail Port: {app.config.get('MAIL_PORT')}
TLS Enabled: {app.config.get('MAIL_USE_TLS')}
Sender: {app.config.get('MAIL_DEFAULT_SENDER')}
Admin Email: {app.config.get('ADMIN_EMAIL')}

If you received this email, your email configuration is correct and all order emails will work properly!

✅ Ready to send:
  - Order confirmations
  - Order status updates
  - Cancellation notifications

---
SecretsClan Store
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        """
        
        print("\n📤 Attempting to send test email...")
        mail.send(msg)
        print("✅ Test email sent successfully!")
        print("="*60 + "\n")
        
        flash('✅ Test email sent successfully! Check your inbox at ' + app.config.get('ADMIN_EMAIL'), 'success')
        
    except Exception as e:
        error_details = f"❌ Email test failed: {str(e)}"
        print("\n" + error_details)
        print("="*60 + "\n")
        
        import traceback
        print(traceback.format_exc())
        
        flash(f'❌ Email test failed: {str(e)}. Check console for details.', 'danger')
    
    return redirect(url_for('admin_dashboard'))


# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
