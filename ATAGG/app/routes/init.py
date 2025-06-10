from flask import Blueprint

# Create blueprints first
main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__)

# Import routes after creating blueprints
from . import main_routes
from . import admin_routes