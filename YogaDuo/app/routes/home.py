
from flask import Blueprint, render_template, request
from app.models import db  # Import the db object
import json
import re

home = Blueprint('home', __name__)

# Function to extract the first image from the blog content
def extract_first_image(content):
    match = re.search(r'<img src="([^\"]+)"', content)
    return match.group(1) if match else None

@home.route('/')
def index():
    try:
        db.ping(reconnect=True)  # Ensure the connection is active
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT id, title, content FROM blogs ORDER BY views DESC LIMIT 5")
        trending_blogs = cursor.fetchall()

        cursor.execute("SELECT id, title, content FROM blogs ORDER BY created_at DESC LIMIT 5")
        latest_blogs = cursor.fetchall()

        cursor.close()

        for blog in trending_blogs:
            blog['image'] = extract_first_image(blog['content'])

        for blog in latest_blogs:
            blog['image'] = extract_first_image(blog['content'])

        return render_template('home.html', trending_blogs=trending_blogs, latest_blogs=latest_blogs)

    except mysql.connector.Error as e:
        return f"Error connecting to the database: {e}", 500


@home.route('/sitemap.xml')
def sitemap():
    return render_template('sitemap.xml')

@home.route('/load_more_blogs', methods=['POST'])
def load_more_blogs():
    offset = int(request.form.get('offset', 0))
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, title, content FROM blogs ORDER BY created_at DESC LIMIT 5 OFFSET %s", (offset,))
    more_blogs = cursor.fetchall()
    cursor.close()

    for blog in more_blogs:
        blog['image'] = extract_first_image(blog['content'])

    return json.dumps(more_blogs)

@home.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    cursor = db.cursor(dictionary=True)  # Fetch results as a dictionary
    cursor.execute("SELECT id, title, content, elements, category, keywords, views FROM blogs WHERE id = %s", (blog_id,))
    blog = cursor.fetchone()

    if not blog:
        cursor.close()
        return "Blog not found", 404

    # Increment the views count
    cursor.execute("UPDATE blogs SET views = views + 1 WHERE id = %s", (blog_id,))
    db.commit()
    cursor.close()

    # Convert JSON elements to a list if needed
    try:
        blog_elements = json.loads(blog["elements"]) if isinstance(blog["elements"], str) else blog["elements"]
    except json.JSONDecodeError:
        blog_elements = [blog["elements"]]  # Treat as plain text if not JSON

    return render_template('blog_detail.html', blog=blog, blog_elements=blog_elements)

@home.route('/about')
def about():
    return render_template('about.html')

@home.route('/contact')
def contact():
    return render_template('contact.html')
