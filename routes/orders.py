"""
Orders Blueprint
Handles all order-related routes for both users and admin
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime

from models import db, Order, OrderItem, Cart
from utils.email_service import send_order_confirmation, send_order_cancellation, send_order_status_update

# Create blueprint
orders_bp = Blueprint('orders', __name__)


def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ============ USER ORDER ROUTES ============

@orders_bp.route('/my-orders')
@login_required
def my_orders():
    """Display user's order history"""
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('my_orders.html', orders=orders)


@orders_bp.route('/my-orders/<int:order_id>')
@login_required
def order_details(order_id):
    """Display detailed view of a specific order"""
    order = db.session.get(Order, order_id)
    
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('orders.my_orders'))
    
    # Ensure user can only view their own orders
    if order.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('orders.my_orders'))
    
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    return render_template('order_details.html', order=order, order_items=order_items)


@orders_bp.route('/my-orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancel an order (only if within 24 hours and status is Pending)"""
    order = db.session.get(Order, order_id)
    
    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('orders.my_orders'))
    
    # Ensure user can only cancel their own orders
    if order.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('orders.my_orders'))
    
    # Check if order can be cancelled
    if not order.can_be_cancelled():
        if order.status != 'Pending':
            flash(f'Cannot cancel order with status "{order.status}". Only pending orders can be cancelled.', 'danger')
        else:
            flash('Cannot cancel order. Cancellation is only allowed within 24 hours of order placement.', 'danger')
        return redirect(url_for('orders.order_details', order_id=order_id))
    
    # Update order status
    order.status = 'Cancelled'
    db.session.commit()
    
    # Send cancellation emails
    from flask import current_app
    try:
        mail = current_app.extensions.get('mail')
        if mail:
            email_sent = send_order_cancellation(mail, order, cancelled_by='customer')
            if email_sent:
                flash('Order cancelled successfully. Confirmation emails have been sent.', 'success')
            else:
                flash('Order cancelled successfully. However, there was an issue sending confirmation emails.', 'warning')
        else:
            flash('Order cancelled successfully.', 'success')
    except Exception as e:
        current_app.logger.error(f"Error sending cancellation emails: {e}")
        flash('Order cancelled successfully. However, there was an issue sending confirmation emails.', 'warning')
    
    return redirect(url_for('orders.my_orders'))


# ============ ADMIN ORDER ROUTES ============

@orders_bp.route('/admin/orders')
@admin_required
def admin_orders():
    """View all orders with optional status filter"""
    status_filter = request.args.get('status', 'all')
    
    if status_filter == 'all':
        orders = Order.query.order_by(Order.order_date.desc()).all()
    else:
        orders = Order.query.filter_by(status=status_filter).order_by(Order.order_date.desc()).all()
    
    # Calculate total revenue from Delivered orders
    total_revenue = db.session.query(db.func.sum(Order.total_price)).filter_by(status='Delivered').scalar() or 0
    
    # Count orders by status
    status_counts = {
        'Pending': Order.query.filter_by(status='Pending').count(),
        'Processing': Order.query.filter_by(status='Processing').count(),
        'Packed': Order.query.filter_by(status='Packed').count(),
        'Shipped': Order.query.filter_by(status='Shipped').count(),
        'Delivered': Order.query.filter_by(status='Delivered').count(),
        'Cancelled': Order.query.filter_by(status='Cancelled').count(),
    }
    
    return render_template('admin_orders.html', 
                         orders=orders, 
                         status_filter=status_filter,
                         total_revenue=total_revenue,
                         status_counts=status_counts)


@orders_bp.route('/admin/orders/<int:id>')
@admin_required
def admin_order_details(id):
    """View order details in admin panel"""
    order = Order.query.get_or_404(id)
    order_items = OrderItem.query.filter_by(order_id=id).all()
    return render_template('admin/order_details.html', order=order, order_items=order_items)


@orders_bp.route('/admin/orders/update_status/<int:id>', methods=['POST'])
@admin_required
def admin_update_order_status(id):
    """Update order status"""
    order = Order.query.get_or_404(id)
    old_status = order.status
    new_status = request.form.get('status')
    
    valid_statuses = ['Pending', 'Processing', 'Packed', 'Shipped', 'Delivered', 'Cancelled']
    
    if new_status in valid_statuses:
        order.status = new_status
        db.session.commit()
        
        # Send status update email to customer
        from flask import current_app
        try:
            mail = current_app.extensions.get('mail')
            if mail and new_status != old_status:
                email_sent = send_order_status_update(mail, order, old_status)
                if email_sent:
                    flash(f'Order status updated to {new_status}. Customer has been notified via email.', 'success')
                else:
                    flash(f'Order status updated to {new_status}. However, there was an issue sending the notification email.', 'warning')
            else:
                flash(f'Order status updated to {new_status}.', 'success')
        except Exception as e:
            current_app.logger.error(f"Error sending status update email: {e}")
            flash(f'Order status updated to {new_status}. However, there was an issue sending the notification email.', 'warning')
    else:
        flash('Invalid status.', 'danger')
    
    return redirect(url_for('orders.admin_order_details', id=id))


@orders_bp.route('/admin/orders/delete/<int:id>')
@admin_required
def admin_delete_order(id):
    """Delete order and its items"""
    order = Order.query.get_or_404(id)
    
    # OrderItems will be automatically deleted due to cascade='all, delete-orphan'
    db.session.delete(order)
    db.session.commit()
    flash('Order deleted successfully!', 'success')
    return redirect(url_for('orders.admin_orders'))
