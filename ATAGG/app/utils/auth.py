from functools import wraps
from flask import current_app, session, redirect, url_for
import csv
import os
from datetime import datetime

def is_admin():
    """Check if current user is admin"""
    return session.get('admin_logged_in', False)

def verify_admin_credentials(username, password):
    """Verify admin credentials against environment variables"""
    return (username == current_app.config['ADMIN_USERNAME'] and 
            password == current_app.config['ADMIN_PASSWORD'])

def admin_required(f):
    """Decorator to restrict routes to admin only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function
