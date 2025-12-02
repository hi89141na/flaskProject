# SecretsClan Order Checkout System - Setup Instructions

## Overview
This update adds a complete order checkout system with Cash on Delivery (COD) and real-time email notifications to the SecretsClan e-commerce application.

## New Features Added

### 1. **Order Management System**
- Order and OrderItem database models
- Order status tracking (Pending, Packed, Shipped, Delivered)
- Customer information collection (name, email, phone, address)

### 2. **Checkout Process**
- Checkout form with validation
- Order summary display
- COD payment method
- Email confirmation to both customer and admin

### 3. **Admin Order Management**
- View all orders with details
- Update order status
- View individual order details and items

## Installation Steps

### 1. Install Required Packages
```bash
pip install -r requirements.txt
```

This will install the new dependency: **Flask-Mail==0.9.1**

### 2. Configure Email Settings

You need to configure Gmail to send emails. Follow these steps:

#### A. Enable 2-Step Verification on Your Google Account
1. Go to your Google Account → Security
2. Enable 2-Step Verification

#### B. Generate App Password
1. Go to Google Account → Security → 2-Step Verification
2. Scroll down to "App passwords"
3. Select "Mail" and "Other (Custom name)"
4. Give it a name (e.g., "SecretsClan Flask App")
5. Copy the 16-character password generated

#### C. Update app.py Configuration
In `app.py`, replace the placeholders with your actual credentials:

```python
# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'secretsclanstore@gmail.com'  # Your Gmail
app.config['MAIL_PASSWORD'] = 'YOUR_16_CHAR_APP_PASSWORD'  # Paste the app password here
app.config['MAIL_DEFAULT_SENDER'] = 'secretsclanstore@gmail.com'
app.config['ADMIN_EMAIL'] = 'hinanadeem@gmail.com'  # Admin email to receive order notifications
```

### 3. Reinitialize Database

Since new models were added, reinitialize the database:

```bash
python init_db.py
```

This will create all necessary tables including Order and OrderItem.

### 4. Run the Application

```bash
python app.py
```

The application will be available at: http://127.0.0.1:5000/

## How to Use

### For Customers:

1. **Browse Products**: View products on homepage or products page
2. **Add to Cart**: Click "Add to Cart" on any product
3. **View Cart**: Click cart icon in navbar
4. **Proceed to Checkout**: Click "Proceed to Checkout" button in cart
5. **Fill Checkout Form**: Enter name, email, phone, and delivery address
6. **Place Order**: Click "Place Order" button
7. **Confirmation**: View order success page and check email for confirmation

### For Admin:

1. **Login**: Use admin credentials (admin@secretsclan.com / admin123)
2. **Access Admin Panel**: Click "Admin Panel" in user menu
3. **View Orders**: Click "Orders" in admin sidebar
4. **View Order Details**: Click the eye icon on any order
5. **Update Status**: Select new status and click "Update Status"

## Email Templates

### Customer Email
```
Dear [Customer Name],

Thank you for shopping with SecretsClan!

Your order has been received and will be processed soon.

Order Details:
Order ID: #[Order ID]
Order Date: [Date and Time]

Order Items:
- [Product Name] x [Quantity] @ Rs. [Price] = Rs. [Subtotal]
...

Total Amount: Rs. [Total]
Payment Method: COD

Delivery Address:
[Customer Address]

Your order will be delivered to the above address.

Thank you for choosing SecretsClan!

Best Regards,
SecretsClan Team
```

### Admin Email
```
A new order has been placed on SecretsClan.

Order ID: #[Order ID]
Customer Name: [Name]
Email: [Email]
Phone: [Phone]
Delivery Address: [Address]

Order Items:
- [Product Name] x [Quantity] @ Rs. [Price] = Rs. [Subtotal]
...

Total Amount: Rs. [Total]
Payment Method: COD
Order Date: [Date and Time]

Please process this order as soon as possible.

---
SecretsClan Admin Panel
```

## New Routes Added

| Route | Method | Description |
|-------|--------|-------------|
| `/checkout` | GET | Display checkout form |
| `/place_order` | POST | Process order and send emails |
| `/order_success` | GET | Display order confirmation |
| `/admin/orders` | GET | View all orders (admin only) |
| `/admin/orders/<id>` | GET | View order details (admin only) |
| `/admin/orders/update_status/<id>` | POST | Update order status (admin only) |

## Database Schema Updates

### Order Table
- `id`: Primary key
- `name`: Customer name
- `email`: Customer email
- `phone`: Customer phone
- `address`: Delivery address
- `total_price`: Total order amount
- `payment_method`: Payment method (default: COD)
- `order_date`: Order timestamp
- `status`: Order status (Pending/Packed/Shipped/Delivered)
- `user_id`: Foreign key to User (optional)

### OrderItem Table
- `id`: Primary key
- `order_id`: Foreign key to Order
- `product_name`: Product name at time of order
- `quantity`: Product quantity
- `price`: Product price at time of order

## Testing the Email Feature

1. **Test Email Configuration**:
   - Place a test order
   - Check if emails are sent to both customer and admin
   - Verify email content

2. **Common Issues**:
   - **"Authentication failed"**: Check if app password is correct
   - **"SMTP connection failed"**: Ensure firewall allows SMTP on port 587
   - **Emails not received**: Check spam/junk folder
   - **Wrong credentials**: Verify MAIL_USERNAME and ADMIN_EMAIL are correct

3. **Debug Mode**:
   If emails fail, check the console output for error messages. The application will still work, but you'll see a warning flash message.

## Important Notes

- **Security**: Never commit your app password to version control. Use environment variables in production.
- **Email Limits**: Gmail has sending limits (100-500 emails per day for free accounts).
- **Order History**: Users can't view their order history yet (future enhancement).
- **Payment**: Only Cash on Delivery (COD) is supported currently.
- **Image Uploads**: Make sure `static/uploads/` directory exists for product images.

## Troubleshooting

### Email Not Sending
```python
# Add this to test email configuration
from flask_mail import Message
from app import app, mail

with app.app_context():
    msg = Message('Test', recipients=['test@example.com'])
    msg.body = 'This is a test email'
    mail.send(msg)
    print('Email sent successfully!')
```

### Database Issues
If you encounter database errors:
```bash
# Delete the old database
# Windows
del instance\secretsclan.db

# Linux/Mac
rm instance/secretsclan.db

# Reinitialize
python init_db.py
```

## Future Enhancements

Potential improvements:
- User order history page
- Order cancellation feature
- Multiple payment methods (credit card, PayPal, etc.)
- Email templates with HTML formatting
- Order tracking system
- Invoice generation (PDF)
- SMS notifications
- Delivery date estimation

## Support

For issues or questions, contact: secretsclanstore@gmail.com

---
**Version**: 2.0 (Order Checkout System)
**Date**: 2024
**Developed for**: Software Construction and Development Course
