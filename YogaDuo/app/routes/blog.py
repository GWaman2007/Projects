from flask import Blueprint, render_template
from app.models import db
import json

blog = Blueprint('blog', __name__)

@blog.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    cursor = db.cursor(dictionary=True)  # Fetch results as a dictionary
    cursor.execute("SELECT id, title, content, elements, category, keywords FROM blogs WHERE id = %s", (blog_id,))
    blog = cursor.fetchone()
    cursor.close()

    if not blog:
        return "Blog not found", 404

    # Convert JSON elements to a list if needed
    try:
        blog_elements = json.loads(blog["elements"]) if isinstance(blog["elements"], str) else blog["elements"]
    except json.JSONDecodeError:
        blog_elements = [blog["elements"]]  # Treat as plain text if not JSON

    return render_template('blog_detail.html', blog=blog, blog_elements=blog_elements)

