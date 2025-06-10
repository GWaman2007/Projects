from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash, session
from functools import wraps
from slugify import slugify
from werkzeug.utils import secure_filename
import os
import csv
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to restrict routes to admin only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the admin credentials are in the session
        if 'admin_username' not in session or session.get('admin_username') != current_app.config['ADMIN_USERNAME']:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == current_app.config['ADMIN_USERNAME'] and password == current_app.config['ADMIN_PASSWORD']:
            session['admin_username'] = username
            session['admin_password'] = password
            print(f"Session data after login: {session}")
            return redirect(url_for('admin.create'))
        flash('Invalid credentials')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    # Clear session data upon logout
    session.pop('admin_username', None)
    session.pop('admin_password', None)
    return redirect(url_for('main.home'))

@admin_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        description = request.form['description']
        keywords = request.form.get('keywords', '').strip()  # Get keywords input

        # Generate slug
        slug = slugify(title)

        # Prepare content
        subtitles = request.form.getlist('subtitle[]')
        contents = request.form.getlist('content[]')

        if len(subtitles) != len(contents):
            flash('Invalid content sections')
            return redirect(url_for('admin.create'))

        content_html = "".join(f"<h2>{s}</h2>\n<p>{c}</p>\n" for s, c in zip(subtitles, contents))

        html_file = f"{slug}.html"
        html_path = os.path.join(current_app.root_path, 'guides', html_file)
        with open(html_path, 'w', encoding='utf-8') as file:
            file.write(content_html)

        # Handle image uploads
        images = request.files.getlist('images')
        image_folder = os.path.join(current_app.root_path, 'guides', 'images', slug)
        os.makedirs(image_folder, exist_ok=True)

        processed_images = []

        for image in images:
            if image.filename:
                filename = secure_filename(image.filename)
                original_path = os.path.join(image_folder, filename)
                image.save(original_path)

                # Resize image to uniform dimensions
                try:
                    from PIL import Image
                    with Image.open(original_path) as img:
                        basewidth = 200
                        wpercent = (basewidth / float(img.size[1]))
                        hsize = int((float(img.size[0]) * float(wpercent)))
                        img_resized = img.resize((hsize, basewidth), Image.LANCZOS)

                        resized_filename = f'resized_{filename}'
                        resized_path = os.path.join(image_folder, resized_filename)
                        img_resized.save(resized_path)

                        # Add resized filename to list
                        processed_images.append(resized_filename)
                except Exception as e:
                    current_app.logger.error(f"Error resizing image {filename}: {e}")
                    flash(f"Error processing image {filename}")

                # Delete the original file after resizing
                if os.path.exists(original_path):
                    os.remove(original_path)

        # Save to CSV
        csv_path = os.path.join(current_app.root_path, 'data', 'posts.csv')

        # Create CSV if it doesn't exist
        if not os.path.exists(csv_path):
            with open(csv_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=[
                    'id', 'title', 'slug', 'description', 'category','keywords',
                    'date', 'modified_date', 'views', 'html_file', 'image_folder', 'images'
                ])
                writer.writeheader()

        # Add new post
        with open(csv_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'id', 'title', 'slug', 'description', 'category','keywords',
                'date', 'modified_date', 'views', 'html_file', 'image_folder', 'images'
            ])
            writer.writerow({
                'id': datetime.now().strftime('%Y%m%d%H%M%S'),
                'title': title,
                'slug': slug,
                'description': description,
                'category': category,
                'keywords': keywords,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'modified_date': datetime.now().strftime('%Y-%m-%d'),
                'views': 0,
                'html_file': html_file,
                'image_folder': f"images/{slug}",
                'images': ','.join(processed_images)
            })

        return redirect(url_for('main.blog_post', slug=slug))

    return render_template('admin/create.html')
@admin_bp.route('/delete-guide', methods=['GET', 'POST'])
@admin_required
def delete_guide():
    guides = []
    csv_path = os.path.join(current_app.root_path, 'data', 'posts.csv')

    # Read all guides from CSV (We assume there's no header or handle headers properly)
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            guides = [(row[0], row[1]) for row in reader]  # (slug, title)

    if request.method == 'POST':
        selected_guide_slug = request.form['guide_slug']

        # Create a temporary CSV file to overwrite the original
        temp_file = os.path.join(current_app.root_path, 'data', 'posts_temp.csv')

        with open(csv_path, 'r', encoding='utf-8') as infile, open(temp_file, 'w', newline='', encoding='utf-8') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            # Read the first row to write headers if any
            headers = next(reader, None)
            if headers:
                writer.writerow(headers)

            guide_found = False
            for row in reader:
                if row[0] == selected_guide_slug:  # Assume slug is in the first column
                    guide_found = True
                    continue  # Skip this row, effectively deleting it
                writer.writerow(row)

        if guide_found:
            # Replace the old CSV with the new one
            os.replace(temp_file, csv_path)

            # Delete the corresponding HTML file
            html_file_path = os.path.join(current_app.root_path, 'guides', 'html', f"{selected_guide_slug}.html")
            if os.path.exists(html_file_path):
                os.remove(html_file_path)

            # Delete the images folder
            image_folder = os.path.join(current_app.root_path, 'guides', 'images', selected_guide_slug)
            if os.path.exists(image_folder):
                for filename in os.listdir(image_folder):
                    file_path = os.path.join(image_folder, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                os.rmdir(image_folder)

            flash(f"Guide '{selected_guide_slug}' and its images have been deleted.", 'success')
        else:
            flash('Guide not found.', 'error')

        return redirect(url_for('admin.delete_guide'))

    return render_template('admin/delete_guide.html', guides=guides)