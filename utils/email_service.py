"""
Email Service for Order Management
Handles all email notifications for orders, cancellations, and status updates
"""
from flask import current_app
from flask_mail import Message
import traceback
import logging

logger = logging.getLogger(__name__)


def send_order_confirmation(mail, order, user):
    """Send order confirmation email to customer and admin"""
    try:
        logger.info(f"📧 Preparing order confirmation email for {user.email}")
        
        sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
        
        # Build order items HTML
        items_html = ""
        items_text = ""
        for item in order.order_items:
            items_html += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">{item.product_name}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{item.quantity}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">₹{item.price:.2f}</td>
                <td style="padding: 8px; border: 1px solid #ddd;">₹{item.get_subtotal():.2f}</td>
            </tr>
            """
            items_text += f"  - {item.product_name} x {item.quantity} @ ₹{item.price:.2f} = ₹{item.get_subtotal():.2f}\n"
        
        # Send email to customer
        customer_msg = Message(
            subject=f'Order Confirmation - #{order.id}',
            recipients=[user.email],
            sender=sender
        )
        
        customer_msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #4CAF50;">Thank you for your order!</h2>
            <p>Dear {user.name},</p>
            <p>Your order <strong>#{order.id}</strong> has been confirmed and is being processed.</p>
            
            <h3>Order Details:</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Product</th>
                        <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Quantity</th>
                        <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Price</th>
                        <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
                <tfoot>
                    <tr style="font-weight: bold; background-color: #f9f9f9;">
                        <td colspan="3" style="padding: 8px; text-align: right; border: 1px solid #ddd;">Total:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">₹{order.total_price:.2f}</td>
                    </tr>
                </tfoot>
            </table>
            
            <h3>Shipping Details:</h3>
            <p>
                <strong>Name:</strong> {order.name}<br>
                <strong>Phone:</strong> {order.phone}<br>
                <strong>Address:</strong> {order.address}<br>
                <strong>Payment Method:</strong> {order.payment_method}
            </p>
            
            <p><strong>Status:</strong> <span style="color: #FF9800; font-weight: bold;">{order.status}</span></p>
            <p>We'll send you another email when your order ships.</p>
            
            <hr style="margin: 20px 0;">
            <p style="color: #666; font-size: 12px;">
                Best regards,<br>
                <strong>SecretsClan Team</strong><br>
                If you have any questions, please contact us.
            </p>
        </div>
        """
        
        logger.info(f"📤 Sending order confirmation to customer: {user.email}...")
        mail.send(customer_msg)
        logger.info(f"✅ Customer confirmation email sent successfully to {user.email}")
        
        # Send email to admin
        admin_msg = Message(
            subject=f'New Order #{order.id} Received - SecretsClan',
            sender=sender,
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
Total Amount: ₹{order.total_price:.2f}
Payment Method: {order.payment_method}

ACTION REQUIRED:
---------------
Please process this order and update the status accordingly.
Login to admin panel: {current_app.config.get('BASE_URL', 'http://localhost:5000')}/admin/orders

---
SecretsClan Order Management System
        """
        
        logger.info(f"📤 Sending admin notification to: {current_app.config['ADMIN_EMAIL']}...")
        mail.send(admin_msg)
        logger.info(f"✅ Admin notification email sent successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send order confirmation email: {str(e)}")
        logger.error(traceback.format_exc())
        return False


def send_order_status_update(mail, order, user, old_status=None):
    """Send order status update email to customer"""
    try:
        logger.info(f"📧 Preparing status update email for order #{order.id}")
        
        sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
        
        msg = Message(
            subject=f'Order Status Update - #{order.id}',
            recipients=[user.email],
            sender=sender
        )
        
        status_color = {
            'Pending': '#FF9800',
            'Processing': '#2196F3',
            'Shipped': '#9C27B0',
            'Delivered': '#4CAF50',
            'Cancelled': '#F44336'
        }.get(order.status, '#666')
        
        status_messages = {
            'Processing': 'Your order is being processed and will be packed soon.',
            'Packed': 'Your order has been packed and is ready for shipment.',
            'Shipped': 'Great news! Your order is on its way to you.',
            'Delivered': 'Your order has been delivered. Thank you for shopping with us!',
            'Cancelled': 'Your order has been cancelled.'
        }
        
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2196F3;">Order Status Update</h2>
            <p>Dear {user.name},</p>
            <p>Your order <strong>#{order.id}</strong> status has been updated.</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                {f'<p style="margin: 0 0 10px 0;"><strong>Previous Status:</strong> {old_status}</p>' if old_status else ''}
                <p style="margin: 0;"><strong>Current Status:</strong> 
                <span style="color: {status_color}; font-size: 18px; font-weight: bold;">{order.status}</span></p>
            </div>
            
            <p style="background-color: #e3f2fd; padding: 10px; border-left: 4px solid #2196F3;">
                {status_messages.get(order.status, 'Your order status has been updated.')}
            </p>
            
            <p><strong>Order Total:</strong> ₹{order.total_price:.2f}</p>
            <p><strong>Payment Method:</strong> {order.payment_method}</p>
            <p><strong>Order Date:</strong> {order.order_date.strftime('%B %d, %Y at %I:%M %p')}</p>
            
            <hr style="margin: 20px 0;">
            <p style="color: #666; font-size: 12px;">
                Thank you for shopping with us!<br>
                <strong>SecretsClan Team</strong>
            </p>
        </div>
        """
        
        logger.info(f"📤 Sending status update to {user.email}...")
        mail.send(msg)
        logger.info(f"✅ Status update email sent successfully to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send status update email: {str(e)}")
        logger.error(traceback.format_exc())
        return False


def send_order_cancellation(mail, order, user, cancelled_by='customer'):
    """Send order cancellation email to customer and admin"""
    try:
        logger.info(f"📧 Preparing cancellation email for order #{order.id}")
        
        sender = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
        
        # Send to customer
        customer_msg = Message(
            subject=f'Order Cancelled - #{order.id}',
            recipients=[user.email],
            sender=sender
        )
        
        customer_msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #F44336;">Order Cancellation</h2>
            <p>Dear {user.name},</p>
            <p>Your order <strong>#{order.id}</strong> has been cancelled.</p>
            
            <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #F44336;">
                <p style="margin: 0;"><strong>Order Amount:</strong> ₹{order.total_price:.2f}</p>
                <p style="margin: 10px 0 0 0; font-size: 14px;">
                    {f'Since this was a Cash on Delivery order, no refund processing is required.' if order.payment_method == 'COD' else 'Refund will be processed within 5-7 business days.'}
                </p>
            </div>
            
            <p><strong>Cancelled By:</strong> {cancelled_by.capitalize()}</p>
            <p><strong>Order Date:</strong> {order.order_date.strftime('%B %d, %Y at %I:%M %p')}</p>
            
            <p>If you have any questions about this cancellation, please don't hesitate to contact our support team.</p>
            
            <hr style="margin: 20px 0;">
            <p style="color: #666; font-size: 12px;">
                Best regards,<br>
                <strong>SecretsClan Team</strong>
            </p>
        </div>
        """
        
        logger.info(f"📤 Sending cancellation email to customer: {user.email}...")
        mail.send(customer_msg)
        logger.info(f"✅ Customer cancellation email sent successfully")
        
        # Notify admin
        items_text = "\n".join([f"  - {item.product_name} x {item.quantity}" for item in order.order_items])
        
        admin_msg = Message(
            subject=f'Order #{order.id} Cancelled - SecretsClan',
            sender=sender,
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
Total Amount: ₹{order.total_price:.2f}
Payment Method: {order.payment_method}

ITEMS IN ORDER:
--------------
{items_text}

---
SecretsClan Order Management System
        """
        
        logger.info(f"📤 Sending admin cancellation notification...")
        mail.send(admin_msg)
        logger.info(f"✅ Admin cancellation notification sent")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send cancellation email: {str(e)}")
        logger.error(traceback.format_exc())
        return False
