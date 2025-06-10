from flask import Flask, render_template
from .config import config
import os

def create_app(config_name='default'):
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])
    app.config['SECRET_KEY'] = '2a0f1f9e135db1ea0ee62e089872fcc6'
    app.config['ADMIN_USERNAME'] = 'AMAN'
    app.config['ADMIN_PASSWORD'] = 'AMAN'



    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from .routes.main_routes import main_bp
    from .routes.admin_routes import admin_bp
    app.register_blueprint(main_bp)  # Public routes
    app.register_blueprint(admin_bp, url_prefix='/admin')  # Admin routes

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html', error_code=404), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html', error_code=500), 500

    # Ensure required directories exist
    directories = ['guides', 'guides/images', 'data']
    for directory in directories:
        os.makedirs(os.path.join(app.root_path, directory), exist_ok=True)

    return app
