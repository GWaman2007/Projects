import os
from flask import Flask, render_template
from flask_session import Session
from config import SECRET_KEY, SESSION_TYPE

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_TYPE'] = SESSION_TYPE
app.template_folder = os.path.join(app.root_path, 'templates')
app.static_folder = os.path.join(app.root_path, 'static')
Session(app)

# Import routes
from app.routes import auth, blog, home ,admin

app.register_blueprint(auth.auth)
app.register_blueprint(blog.blog)
app.register_blueprint(home.home)
app.register_blueprint(admin.admin)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
