from flask import Blueprint, render_template, request, redirect, session, flash
from app.models import db
import os
import json

admin = Blueprint('admin', __name__)

UPLOAD_FOLDER = 'app/static/images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists

@admin.route('/admin', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash('Please login as admin before accessing dashboard!', 'error')
        return redirect('/login')

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT is_admin FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    if not user or not user['is_admin']:
        flash('Please login as admin before accessing dashboard!', 'error')
        return redirect('/')

    if request.method == 'POST':
        title = request.form['title']
        elements = request.form.getlist('elements[]')
        images = request.files.getlist('images[]')
        content = ''
        json_elements = []  # List to store JSON elements

        processed_images = set()  # Set to keep track of processed images

        for element in elements:
            if element.startswith('Subtitle: '):
                content += f'<h2>{element[10:]}</h2>'
                json_elements.append({'type': 'subtitle', 'content': element[10:]})
            elif element.startswith('Paragraph: '):
                content += f'<p>{element[11:]}</p>'
                json_elements.append({'type': 'paragraph', 'content': element[11:]})
            elif element.startswith('Image: '):
                image_name = element[7:]
                if image_name not in processed_images:
                    for image in images:
                        if image.filename == image_name:
                            filename = image.filename.replace(" ", "_")  # Replace spaces to avoid URL issues
                            image_path = os.path.join(UPLOAD_FOLDER, filename)
                            print(f"Saving image to: {image_path}")  # Debugging statement
                            if not os.path.exists(image_path):
                                image.save(image_path)
                            content += f'<img src="..\static\images\{filename}" alt="Image">'
                            json_elements.append({'type': 'image', 'content': filename})
                            processed_images.add(image_name)  # Mark image as processed

        category = request.form['category']
        keywords = request.form['keywords']
        user_id = session['user_id']

        cursor = db.cursor()
        cursor.execute("INSERT INTO blogs (user_id, title, content, category, keywords, elements) VALUES (%s, %s, %s, %s, %s, %s)",
                       (user_id, title, content, category, keywords, json.dumps(json_elements)))
        db.commit()
        cursor.close()
        flash('Blog Post was Successful!', 'success')
        return redirect('/admin')

    cursor = db.cursor()
    cursor.execute("SELECT id, title, content, category, keywords, created_at FROM blogs")
    blogs = cursor.fetchall()
    cursor.close()  # Close the cursor after fetching the data

    return render_template('dashboard.html', blogs=blogs)

@admin.route('/delete_blog/<int:blog_id>', methods=['POST'])
def delete_blog(blog_id):
    if 'user_id' not in session:
        flash('Please login as admin before accessing dashboard!', 'error')
        return redirect('/login') # Redirect to login if user is not logged in

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT is_admin FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone() # Fetch the user from the database

    if not user or not user['is_admin']:
        flash('Please login as admin before accessing dashboard!', 'error')
        return redirect('/')  # Redirect to home if user is not an admin
    cursor = db.cursor()
    cursor.execute("DELETE FROM blogs WHERE id = %s", (blog_id,))
    db.commit()
    cursor.close()
    flash('Blog Post was Successfully deleted!', 'success')
    return redirect('/admin')
