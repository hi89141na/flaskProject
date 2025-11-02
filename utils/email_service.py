"""
Email Service for Order Management
Handles all email notifications for orders, cancellations, and status updates
"""
from flask import current_app
from flask_mail import Message
import traceback


def send_order_confirmation(mail, order, order_items):
    """
    Send order confirmation emails to both customer and admin
    
    Args:
        mail: Flask-Mail instance
        order: Order object
        order_items: List of OrderItem objects
    
    Returns:
        bool: True if emails sent successfully, False otherwise
    """
    try:
        # Prepare order items list for email
        items_text = "\n".join([
            f"  - {item.product_name} x {item.quantity} @ Rs. {item.price:.2f} = Rs. {item.get_subtotal():.2f}"
            for item in order_items
        ])
        
        # Send email to admin
        admin_msg = Message(
            subject=f'New Order #{order.id} Received - SecretsClan',
            recipients=[current_app.config['ADMIN_EMAIL']]
        )
        admin_msg.body = f"""
New Order Received!

ORDER DETAILS:
--------------
Order ID: #{order.id}
Order Date: {order.order_date.strftime('%B %d, %Y at %I:%M %p')}
Status: {order.status}

CUSTOMER INFORMATION:
--------------------
Name: {order.name}
Email: {order.email}
Phone: {order.phone}
Delivery Address: 
{order.address}

ORDER ITEMS:
-----------
{items_text}

PAYMENT:
--------
Total Amount: Rs. {order.total_price:.2f}
Payment Method: {order.payment_method} (Cash on Delivery)

ACTION REQUIRED:
---------------
Please process this order and update the status accordingly.
Login to admin panel: {current_app.config.get('BASE_URL', 'http://localhost:5000')}/admin/orders

---
SecretsClan Order Management System
        """
        mail.send(admin_msg)
        
        # Send email to customer
        customer_msg = Message(
            subject=f'Order Confirmation #{order.id} - SecretsClan',
            recipients=[order.email]
        )
        customer_msg.body = f"""
Dear {order.name},

Thank you for shopping with SecretsClan!

Your order has been successfully placed and will be processed shortly.

ORDER SUMMARY:
--------------
Order ID: #{order.id}
Order Date: {order.order_date.strftime('%B %d, %Y at %I:%M %p')}
Status: {order.status}

ITEMS ORDERED:
-------------
{items_text}

TOTAL AMOUNT: Rs. {order.total_price:.2f}
Payment Method: {order.payment_method} (Cash on Delivery)

DELIVERY DETAILS:
----------------
Delivery Address:
{order.address}

Contact Phone: {order.phone}

EXPECTED DELIVERY:
-----------------
Your order will be delivered within 3-5 business days. You will receive updates via email as your order progresses.

PAYMENT:
--------
You will pay Rs. {order.total_price:.2f} in cash when you receive your order.

NEED HELP?
----------
If you have any questions, please contact us at:
Email: {current_app.config['MAIL_USERNAME']}
Phone: {order.phone}

You can view your order status anytime at: {current_app.config.get('BASE_URL', 'http://localhost:5000')}/my_orders

Thank you for choosing SecretsClan!

Best Regards,
The SecretsClan Team

---
This is an automated email. Please do not reply directly to this message.
        """
        mail.send(customer_msg)
        
        return True
        
    except Exception as e:
        # Log detailed error with traceback
        error_msg = f"Error sending order confirmation emails: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        current_app.logger.error(error_msg)
        return False


def send_order_cancellation(mail, order, cancelled_by='customer'):
    """
    Send order cancellation notification to both customer and admin
    
    Args:
        mail: Flask-Mail instance
        order: Order object
        cancelled_by: str - 'customer' or 'admin'
    
    Returns:
        bool: True if emails sent successfully, False otherwise
    """
    try:
        # Notify admin about cancellation
        admin_msg = Message(
            subject=f'Order #{order.id} Cancelled - SecretsClan',
            recipients=[current_app.config['ADMIN_EMAIL']]
        )
        admin_msg.body = f"""
Order Cancellation Notice

ORDER DETAILS:
--------------
Order ID: #{order.id}
Order Date: {order.order_date.strftime('%B %d, %Y at %I:%M %p')}
Cancelled By: {cancelled_by.capitalize()}
Status: {order.status}

CUSTOMER INFORMATION:
--------------------
Name: {order.name}
Email: {order.email}
Phone: {order.phone}

ORDER VALUE:
-----------
Total Amount: Rs. {order.total_price:.2f}
Payment Method: {order.payment_method}

ITEMS IN ORDER:
--------------
{chr(10).join([f"  - {item.product_name} x {item.quantity}" for item in order.order_items])}

---
SecretsClan Order Management System
        """
        mail.send(admin_msg)
        
        # Notify customer about cancellation
        customer_msg = Message(
            subject=f'Order #{order.id} Cancellation Confirmation - SecretsClan',
            recipients=[order.email]
        )
        customer_msg.body = f"""
Dear {order.name},

Your order has been cancelled successfully.

ORDER DETAILS:
--------------
Order ID: #{order.id}
Order Date: {order.order_date.strftime('%B %d, %Y at %I:%M %p')}
Status: Cancelled
Total Amount: Rs. {order.total_price:.2f}

CANCELLED ITEMS:
---------------
{chr(10).join([f"  - {item.product_name} x {item.quantity} - Rs. {item.get_subtotal():.2f}" for item in order.order_items])}

{'Since this was a Cash on Delivery order, no refund processing is required.' if order.payment_method == 'COD' else 'Refund will be processed within 5-7 business days.'}

We're sorry to see you cancel this order. If you faced any issues, please let us know so we can improve our service.

NEED ASSISTANCE?
---------------
If you have any questions, please contact us at:
Email: {current_app.config['MAIL_USERNAME']}

Thank you for considering SecretsClan.

Best Regards,
The SecretsClan Team

---
This is an automated email. Please do not reply directly to this message.
        """
        mail.send(customer_msg)
        
        return True
        
    except Exception as e:
        error_msg = f"Error sending cancellation emails: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        current_app.logger.error(error_msg)
        return False


def send_order_status_update(mail, order, old_status):
    """
    Send order status update notification to customer
    
    Args:
        mail: Flask-Mail instance
        order: Order object
        old_status: str - Previous status
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        status_messages = {
            'Processing': 'Your order is being processed and will be packed soon.',
            'Packed': 'Your order has been packed and is ready for shipment.',
            'Shipped': 'Great news! Your order is on its way to you.',
            'Delivered': 'Your order has been delivered. Thank you for shopping with us!',
            'Cancelled': 'Your order has been cancelled.'
        }
        
        customer_msg = Message(
            subject=f'Order #{order.id} Status Update: {order.status} - SecretsClan',
            recipients=[order.email]
        )
        customer_msg.body = f"""
Dear {order.name},

Your order status has been updated!

ORDER DETAILS:
--------------
Order ID: #{order.id}
Previous Status: {old_status}
Current Status: {order.status}

STATUS UPDATE:
-------------
{status_messages.get(order.status, 'Your order status has been updated.')}

ORDER SUMMARY:
-------------
Total Amount: Rs. {order.total_price:.2f}
Payment Method: {order.payment_method}
Order Date: {order.order_date.strftime('%B %d, %Y at %I:%M %p')}

DELIVERY ADDRESS:
----------------
{order.address}

{'PAYMENT DUE: Rs. ' + f'{order.total_price:.2f}' + ' (Cash on Delivery)' if order.status == 'Delivered' and order.payment_method == 'COD' else ''}

You can track your order anytime at: {current_app.config.get('BASE_URL', 'http://localhost:5000')}/my_orders

NEED HELP?
----------
If you have any questions, please contact us at:
Email: {current_app.config['MAIL_USERNAME']}
Phone: {order.phone}

Thank you for shopping with SecretsClan!

Best Regards,
The SecretsClan Team

---
This is an automated email. Please do not reply directly to this message.
        """
        mail.send(customer_msg)
        
        return True
        
    except Exception as e:
        error_msg = f"Error sending status update email: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        current_app.logger.error(error_msg)
        return False
