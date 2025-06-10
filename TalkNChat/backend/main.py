from flask import Flask, request, render_template, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import bcrypt
import datetime
import json
import os
import uuid
import logging

# Configuration
USER_FILE = "users.json"
CHAT_FILE = "chats.json"
UPLOAD_DIR = "/home/talknchat/uploads"
SECRET_KEY = "63de277d22f576339f8e0635e9868005424ce6da11bbded66a9411b45cac8fe9"  # Should be an environment variable in production

app = Flask(__name__,
            static_folder="../frontend/static",
            template_folder="../frontend/templates")
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB limit

# Initialize JSON files and upload directory if they don't exist
def initialize_files():
    """Initialize necessary files and directories on application startup."""
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            json.dump([], f)

    if not os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "w") as f:
            json.dump([], f)

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

initialize_files()

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# User management functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def get_user(username: str):
    """Fetch a user from the JSON file."""
    try:
        with open(USER_FILE, "r") as f:
            users = json.load(f)
            for user in users:
                if user["username"] == username:
                    return user
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
    return None

def save_user(user: dict):
    """Save a user to the JSON file."""
    try:
        with open(USER_FILE, "r") as f:
            users = json.load(f)
        users.append(user)
        with open(USER_FILE, "w") as f:
            json.dump(users, f)
        return True
    except Exception as e:
        logger.error(f"Error saving user: {str(e)}")
        return False

# Chat management functions
def save_chat_message(message: dict):
    """Save a chat message to the JSON file."""
    try:
        with open(CHAT_FILE, "r") as f:
            chats = json.load(f)
        chats.append(message)
        with open(CHAT_FILE, "w") as f:
            json.dump(chats, f)
        return True
    except Exception as e:
        logger.error(f"Error saving chat message: {str(e)}")
        return False

def get_messages_between_users(user1: str, user2: str):
    """Get all messages between two users."""
    try:
        with open(CHAT_FILE, "r") as f:
            chats = json.load(f)
            messages = []
            for chat in chats:
                if (chat["sender"] == user1 and chat["recipient"] == user2) or \
                   (chat["sender"] == user2 and chat["recipient"] == user1):
                    messages.append({
                        "timestamp": chat["timestamp"],
                        "username": chat["sender"],
                        "message": chat["message"],
                        "file_url": chat.get("file_url")
                    })
            return messages
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        return []

def get_messaged_users(username: str):
    """Get all users that a user has messaged or received messages from."""
    try:
        with open(CHAT_FILE, "r") as f:
            chats = json.load(f)
            users = set()
            for chat in chats:
                if chat["sender"] == username:
                    users.add(chat["recipient"])
                elif chat["recipient"] == username:
                    users.add(chat["sender"])
            return list(users)
    except Exception as e:
        logger.error(f"Error getting messaged users: {str(e)}")
        return []

def search_users(query: str):
    """Search users by username."""
    try:
        with open(USER_FILE, "r") as f:
            users = json.load(f)
            matched_users = [user["username"] for user in users if query.lower() in user["username"].lower()]
            return matched_users
    except Exception as e:
        logger.error(f"Error searching users: {str(e)}")
        return []

# Route handlers
@app.route('/')
def home_page():
    """Home page route."""
    username = session.get("username")
    return render_template("home.html", username=username)

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.static_folder, "sitemap.xml", mimetype="application/xml")

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = get_user(username)
        if user and verify_password(password, user["hashed_password"]):
            session["username"] = username
            return redirect(url_for('dashboard'))
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    return render_template("login.html")

@app.route("/robots.txt")
def robots_txt():
    return "User-agent: *\nAllow: /\nSitemap: https://talknchat.pythonanywhere.com/sitemap.xml", 200, {"Content-Type": "text/plain"}

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page and user creation."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if get_user(username):
            return jsonify({"error": "Username already exists"}), 400

        hashed_password = hash_password(password)
        new_user = {"username": username, "hashed_password": hashed_password}

        if save_user(new_user):
            return redirect(url_for('login'))
        else:
            return jsonify({"error": "Failed to create user"}), 500

    return render_template("register.html")

@app.route('/logout')
def logout():
    """Logout and clear session."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    """Dashboard page for logged-in users."""
    username = session.get("username")
    if not username:
        return redirect(url_for('login'))

    return render_template("dashboard.html", username=username)

@app.route('/get-username')
def get_username():
    """Get the current logged-in username."""
    username = session.get("username")
    if not username:
        return jsonify({"error": "Not logged in"}), 401

    return jsonify({"username": username})

@app.route('/get-messaged-users')
def get_messaged_users_route():
    """Get all users that the current user has messaged or received messages from."""
    username = session.get("username")
    if not username:
        return jsonify({"error": "Not logged in"}), 401

    users = get_messaged_users(username)
    return jsonify({"users": users})

@app.route('/get-messages/<recipient>')
def get_messages_route(recipient):
    """Get all messages between the current user and a recipient."""
    username = session.get("username")
    if not username:
        return jsonify({"error": "Not logged in"}), 401

    messages = get_messages_between_users(username, recipient)
    return jsonify({"messages": messages})

@app.route('/poll-messages/<recipient>')
def poll_messages(recipient):
    """Poll for new messages between the current user and a recipient."""
    username = session.get("username")
    if not username:
        return jsonify({"error": "Not logged in"}), 401

    messages = get_messages_between_users(username, recipient)
    return jsonify({"messages": messages})

@app.route('/search-users')
def search_users_route():
    """Search users by username."""
    query = request.args.get('query', '')
    matched_users = search_users(query)
    return jsonify({"users": matched_users})

@app.route('/send-message', methods=['POST'])
def send_message():
    """Send a message to another user."""
    username = session.get("username")
    if not username:
        return jsonify({"error": "Not logged in"}), 401

    recipient = request.args.get('recipient')
    message = request.form.get('message')
    file = request.files.get('file')

    if not recipient:
        return jsonify({"error": "Recipient is required"}), 400

    if not message and not file:
        return jsonify({"error": "Message or file is required"}), 400

    # Replace line breaks with <br> for proper display
    if message:
        message = message.replace('\n', '<br>')
    else:
        message = ""

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_message = {
        "id": str(uuid.uuid4()),
        "timestamp": timestamp,
        "sender": username,
        "recipient": recipient,
        "message": message
    }

    # Handle file upload
    if file and file.filename:
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            new_message["file_url"] = f"/uploads/{filename}"
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            return jsonify({"error": f"Failed to upload file: {str(e)}"}), 500

    if save_chat_message(new_message):
        return jsonify({"status": "Message sent"})
    else:
        return jsonify({"error": "Failed to send message"}), 500

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory("uploads", filename)
@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(e)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)