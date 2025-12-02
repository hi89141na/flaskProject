# Complete Modular Order Management System Documentation

## Overview
This documentation describes the modular order management system with COD (Cash on Delivery) and email notifications that has been implemented for SecretsClan Flask eCommerce website.

---

## 🏗️ Architecture Overview

The order management system follows a **modular architecture** with clear separation of concerns:

```
SecretsClan/
├── models.py                    # Database models
├── app.py                       # Main application (routes moved to blueprints)
├── routes/
│   ├── __init__.py             # Blueprint initialization
│   └── orders.py               # Order management blueprint
├── utils/
│   └── email_service.py        # Email notification service
└── templates/
    ├── my_orders.html          # User order list
    ├── order_details.html      # User order details
    └── admin_orders.html       # Admin order management
```

---

## 📦 Components

### 1. **Database Models** (`models.py`)

#### Order Model
```python
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='COD')
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Pending')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    order_items = db.relationship('OrderItem', cascade='all, delete-orphan')
```

#### OrderItem Model
```python
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
```

#### Helper Methods Added

**1. `Order.can_be_cancelled()`**
- Checks if order can be cancelled
- Returns `True` if:
  - Status is 'Pending'
  - Order was placed within last 24 hours
- Returns `False` otherwise

**2. `Order.calculate_total()`**
- Calculates total amount from order items
- Returns sum of all item subtotals

**3. `Order.get_status_badge_class()`**
- Returns Bootstrap CSS class for status badge
- Maps status to color:
  - Pending → `bg-warning text-dark` (Yellow)
  - Processing → `bg-info` (Light Blue)
  - Packed → `bg-info` (Light Blue)
  - Shipped → `bg-primary` (Blue)
  - Delivered → `bg-success` (Green)
  - Cancelled → `bg-danger` (Red)

**4. `OrderItem.get_subtotal()`**
- Calculates subtotal for individual item
- Returns `price * quantity`

---

### 2. **Email Service** (`utils/email_service.py`)

#### Functions

**1. `send_order_confirmation(mail, order, order_items)`**
- Sends confirmation emails to both customer and admin
- **To Customer**: Order details, expected delivery, payment info
- **To Admin**: Complete order info with customer details
- **Error Handling**: Try-except with detailed logging
- **Returns**: `True` on success, `False` on failure

**2. `send_order_cancellation(mail, order, cancelled_by='customer')`**
- Sends cancellation notifications
- **To Customer**: Cancellation confirmation
- **To Admin**: Cancellation notice with reason
- **Error Handling**: Graceful failure with logging
- **Returns**: `True` on success, `False` on failure

**3. `send_order_status_update(mail, order, old_status)`**
- Sends status change notification to customer
- Includes status-specific messages
- **Error Handling**: Logs errors but doesn't block order update
- **Returns**: `True` on success, `False` on failure

#### Email Templates

**Admin Order Notification:**
```
Subject: New Order #123 Received - SecretsClan

ORDER DETAILS:
--------------
Order ID: #123
Order Date: [Date & Time]
Status: Pending

CUSTOMER INFORMATION:
--------------------
Name: [Customer Name]
Email: [Customer Email]
Phone: [Customer Phone]
Delivery Address: [Full Address]

ORDER ITEMS:
-----------
- Product Name x Quantity @ Rs. Price = Rs. Subtotal
...

PAYMENT:
--------
Total Amount: Rs. [Total]
Payment Method: COD (Cash on Delivery)

ACTION REQUIRED:
---------------
Please process this order and update the status accordingly.
```

**Customer Confirmation:**
```
Subject: Order Confirmation #123 - SecretsClan

Dear [Customer Name],

Thank you for shopping with SecretsClan!

Your order has been successfully placed and will be processed shortly.

ORDER SUMMARY:
--------------
Order ID: #123
Order Date: [Date & Time]
Status: Pending

ITEMS ORDERED:
-------------
- Product Name x Quantity @ Rs. Price = Rs. Subtotal
...

TOTAL AMOUNT: Rs. [Total]
Payment Method: COD (Cash on Delivery)

EXPECTED DELIVERY:
-----------------
Your order will be delivered within 3-5 business days.

PAYMENT:
--------
You will pay Rs. [Total] in cash when you receive your order.
```

---

### 3. **Orders Blueprint** (`routes/orders.py`)

#### User Routes

**1. `/my-orders` (GET)**
- **Function**: `my_orders()`
- **Auth**: `@login_required`
- **Purpose**: Display user's order history
- **Returns**: Renders `my_orders.html` with user's orders

**2. `/my-orders/<order_id>` (GET)**
- **Function**: `order_details(order_id)`
- **Auth**: `@login_required`
- **Purpose**: Display detailed order information
- **Security**: Verifies user owns the order
- **Returns**: Renders `order_details.html`

**3. `/my-orders/<order_id>/cancel` (POST)**
- **Function**: `cancel_order(order_id)`
- **Auth**: `@login_required`
- **Purpose**: Cancel an order
- **Validation**:
  - User must own the order
  - Order must be cancellable (within 24 hours, status=Pending)
- **Actions**:
  - Updates status to 'Cancelled'
  - Sends cancellation emails
- **Returns**: Redirects to order list

#### Admin Routes

**4. `/admin/orders` (GET)**
- **Function**: `admin_orders()`
- **Auth**: `@admin_required`
- **Purpose**: View all orders with filtering
- **Query Params**: `?status=all|Pending|Processing|Packed|Shipped|Delivered|Cancelled`
- **Features**:
  - Status filtering
  - Revenue calculation (Delivered orders only)
  - Status counts for dashboard
- **Returns**: Renders `admin_orders.html`

**5. `/admin/orders/<id>` (GET)**
- **Function**: `admin_order_details(id)`
- **Auth**: `@admin_required`
- **Purpose**: View detailed order information
- **Returns**: Renders `admin/order_details.html`

**6. `/admin/orders/update_status/<id>` (POST)**
- **Function**: `admin_update_order_status(id)`
- **Auth**: `@admin_required`
- **Purpose**: Update order status
- **Valid Statuses**: Pending, Processing, Packed, Shipped, Delivered, Cancelled
- **Actions**:
  - Updates order status
  - Sends status update email to customer
- **Returns**: Redirects to order details

**7. `/admin/orders/delete/<id>` (GET)**
- **Function**: `admin_delete_order(id)`
- **Auth**: `@admin_required`
- **Purpose**: Delete order and all related items
- **Note**: OrderItems cascade deleted automatically
- **Returns**: Redirects to orders list

---

### 4. **Templates**

#### User Templates

**`my_orders.html`**
- Lists all user's orders
- Shows: Order ID, Date, Status badge, Total, Payment method
- Preview of order items (first 3)
- "View Details" button
- "Cancel Order" button (if eligible)
- Empty state with "Start Shopping" CTA

**`order_details.html`**
- Complete order information
- Order and delivery details
- Itemized list with subtotals
- Status information with description
- Cancel button in header (if eligible)
- Help section with contact info

#### Admin Template

**`admin_orders.html`**
- Revenue dashboard card
- Status summary with counts
- Filter buttons for all statuses
- Orders table with:
  - All order information
  - Color-coded status badges
  - View Details button
  - Delete button
- Shows filtered count

---

## 🔧 Configuration

### Email Configuration (`app.py`)

```python
# Email configuration (Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'  # Use Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'
app.config['ADMIN_EMAIL'] = 'admin@gmail.com'
app.config['BASE_URL'] = 'http://localhost:5000'  # Optional: for email links
```

### Blueprint Registration (`app.py`)

```python
# Register blueprints
from routes import orders_bp
app.register_blueprint(orders_bp)
```

---

## 🔐 Security Features

### 1. **Authentication & Authorization**
- `@login_required` decorator for user routes
- `@admin_required` decorator for admin routes
- User can only view/cancel their own orders
- Admin has full access to all orders

### 2. **Order Cancellation Rules**
- Only within 24 hours of placement
- Only if status is 'Pending'
- Confirmation dialog before cancellation

### 3. **Database Integrity**
- Cascade delete ensures no orphaned OrderItems
- Foreign key constraints maintained
- Transaction rollback on errors

### 4. **Email Error Handling**
- Try-except blocks around all email operations
- Detailed error logging with traceback
- Orders saved even if email fails
- User informed of email status

---

## 📧 Email Notification Flow

### Order Placement
```
User clicks "Place Order"
    ↓
Order created in database
    ↓
Cart cleared
    ↓
send_order_confirmation() called
    ↓
Email to Admin (order notification)
Email to Customer (order confirmation)
    ↓
Success/Warning message to user
    ↓
Redirect to order success page
```

### Order Cancellation
```
User clicks "Cancel Order"
    ↓
Validation checks (24hr, status=Pending)
    ↓
Status updated to 'Cancelled'
    ↓
send_order_cancellation() called
    ↓
Email to Admin (cancellation notice)
Email to Customer (cancellation confirmation)
    ↓
Success message to user
    ↓
Redirect to order list
```

### Status Update (Admin)
```
Admin updates status
    ↓
Status saved to database
    ↓
send_order_status_update() called
    ↓
Email to Customer (status update)
    ↓
Success message to admin
    ↓
Redirect to order details
```

---

## 🧪 Testing Guide

### User Order Tests

1. **Place Order**:
   - Add products to cart
   - Proceed to checkout
   - Fill delivery information
   - Click "Place Order"
   - Verify emails received (customer + admin)

2. **View Orders**:
   - Navigate to "My Orders"
   - Verify all orders displayed
   - Check status badges are correct
   - Click "View Details"

3. **Cancel Order**:
   - Find a recent Pending order
   - Click "Cancel Order"
   - Confirm cancellation
   - Verify status changed
   - Check cancellation emails

4. **Cannot Cancel** (should fail gracefully):
   - Try to cancel old order (>24 hours)
   - Try to cancel Shipped order
   - Verify error messages

### Admin Tests

1. **View All Orders**:
   - Navigate to Admin → Orders
   - Verify revenue displayed
   - Verify status counts
   - Test filter buttons

2. **Update Status**:
   - Open order details
   - Change status using dropdown
   - Click "Update Status"
   - Verify status changed
   - Check customer received email

3. **Delete Order**:
   - Click delete button
   - Confirm deletion
   - Verify order removed
   - Verify OrderItems also deleted

### Email Tests

1. **With Email Configured**:
   - Verify all emails sent successfully
   - Check email content and formatting
   - Verify both customer and admin receive emails

2. **Without Email Configured**:
   - Set invalid email credentials
   - Place order
   - Verify order still saved
   - Verify warning message shown
   - Check error logged in console

---

## 🎯 Key Features Summary

✅ **Modular Architecture**
- Separate blueprints for routes
- Dedicated email service module
- Clear separation of concerns

✅ **Complete Order Management**
- User order history with details
- Admin dashboard with filtering
- Status tracking and updates

✅ **Cash on Delivery (COD)**
- Single payment method
- Payment collected on delivery
- Revenue tracking for delivered orders

✅ **Email Notifications**
- Order confirmation (customer + admin)
- Order cancellation notifications
- Status update notifications
- Graceful failure handling

✅ **User Features**
- View order history
- View order details
- Cancel orders (within 24 hours)
- Track order status

✅ **Admin Features**
- View all orders
- Filter by status
- Update order status
- Delete orders
- Revenue dashboard
- Status statistics

✅ **Security**
- Authentication required
- Authorization checks
- User can only access own orders
- Admin-only routes protected

✅ **Error Handling**
- Try-except blocks
- Detailed error logging
- User-friendly error messages
- No crashes on email failures

---

## 🚀 Usage Examples

### For Customers

**View Order History:**
```
Login → Click "My Orders" → See all orders with status
```

**Cancel Order:**
```
My Orders → View Details → Cancel Order button → Confirm
```

**Track Order:**
```
My Orders → Check status badge color
- Yellow (Pending): Being prepared
- Light Blue (Processing/Packed): Ready for shipping
- Blue (Shipped): On the way
- Green (Delivered): Completed
- Red (Cancelled): Cancelled
```

### For Admins

**Manage Orders:**
```
Admin Panel → Orders → See all orders + revenue + stats
```

**Filter Orders:**
```
Orders → Click status filter button → See filtered orders
```

**Update Status:**
```
Orders → View Details → Select new status → Update
```

**Delete Order:**
```
Orders → Delete button → Confirm deletion
```

---

## 📊 Order Status Workflow

```
Pending → Processing → Packed → Shipped → Delivered
   ↓                                              
Cancelled (only from Pending, within 24h)
```

**Status Descriptions:**
- **Pending**: Order received, awaiting processing
- **Processing**: Order being prepared
- **Packed**: Order packed and ready for shipment
- **Shipped**: Order dispatched to customer
- **Delivered**: Order delivered successfully
- **Cancelled**: Order cancelled by user or admin

---

## 🔮 Future Enhancements

Potential improvements:
- Order search functionality
- Date range filtering
- Export orders to CSV/Excel
- Print invoice feature
- Multiple payment methods
- Order tracking with carrier
- SMS notifications
- Customer reviews
- Return/refund management
- Automated status updates
- Order analytics dashboard
- Email HTML templates
- Order notes/comments
- Bulk status updates

---

## 📝 Files Modified/Created

### Modified:
1. `models.py` - Added helper methods to Order model
2. `app.py` - Registered blueprint, updated email function
3. `templates/base.html` - Updated navbar links
4. `templates/admin/base.html` - Updated sidebar links
5. `templates/my_orders.html` - Added cancel button
6. `templates/order_details.html` - Added cancel button and status info
7. `templates/admin/order_details.html` - Added Processing and Cancelled status options

### Created:
8. `routes/__init__.py` - Blueprint package initialization
9. `routes/orders.py` - Complete orders blueprint
10. `utils/email_service.py` - Email notification service
11. `templates/admin_orders.html` - Admin order management page

---

**Version**: 4.0 (Modular Order Management)  
**Date**: November 3, 2025  
**Status**: Production Ready ✅  
**Architecture**: Modular with Blueprints ✅
