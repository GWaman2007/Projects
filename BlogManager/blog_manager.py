from flask import Flask, request, render_template, redirect, url_for, session, flash, send_from_directory
from mysql.connector import connect
import os
from dotenv import load_dotenv

load_dotenv('.env.txt')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Database connection context manager
def get_db_connection():
    conn = connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME')
    )
    return conn

# Routes
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM blogs ORDER BY id DESC")
    blogs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', blogs=blogs)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and user[2] == password:  # Assuming user[2] is the password column
            session['username'] = username
            session['is_admin'] = user[3]  # Assuming user[3] is is_admin column
            cursor.close()
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')  # Flash error message
            cursor.close()
            conn.close()
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Username already exists', 'error')  # Flash error message
            cursor.close()
            conn.close()
            return redirect(url_for('register'))
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            session['username'] = username
            flash('Registration successful!', 'success')  # Flash success message
            cursor.close()
            conn.close()
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/like/<int:blog_id>', methods=['POST'])
def like(blog_id):
    if 'username' not in session:
        flash('You need to be logged in to like posts.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get user ID from session
    cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
    user = cursor.fetchone()
    user_id = user[0]

    # Check if the user has already liked this post
    cursor.execute("SELECT * FROM blog_likes WHERE blog_id = %s AND user_id = %s", (blog_id, user_id))
    like_exists = cursor.fetchone()

    if not like_exists:
        cursor.execute("INSERT INTO blog_likes (blog_id, user_id) VALUES (%s, %s)", (blog_id, user_id))
        cursor.execute("UPDATE blogs SET like_count = like_count + 1 WHERE id = %s", (blog_id,))
        flash('Blog post liked!')
    else:
        flash('You have already liked this post.')

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('index'))

@app.route('/unlike/<int:blog_id>', methods=['POST'])
def unlike(blog_id):
    if 'username' not in session:
        flash('You need to be logged in to unlike posts.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get user ID from session
    cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
    user = cursor.fetchone()
    user_id = user[0]

    # Check if the user has liked this post
    cursor.execute("SELECT * FROM blog_likes WHERE blog_id = %s AND user_id = %s", (blog_id, user_id))
    like_exists = cursor.fetchone()

    if like_exists:
        cursor.execute("DELETE FROM blog_likes WHERE blog_id = %s AND user_id = %s", (blog_id, user_id))
        cursor.execute("UPDATE blogs SET like_count = like_count - 1 WHERE id = %s", (blog_id,))
        flash('Blog post unliked!')
    else:
        flash('You have not liked this post.')

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('index'))

@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        if 'title' in request.form and 'content' in request.form:
            title = request.form['title']
            content = request.form['content']
            username = session['username']
            cursor.execute("INSERT INTO blogs (title, content, username) VALUES (%s, %s, %s)", (title, content, username))
            conn.commit()
            flash('Blog post created.')

        if 'delete' in request.form:
            blog_id = request.form['delete']

            # Delete likes associated with the blog first to avoid foreign key constraint error
            cursor.execute("DELETE FROM blog_likes WHERE blog_id = %s", (blog_id,))

            # Now delete the blog
            cursor.execute("DELETE FROM blogs WHERE id = %s", (blog_id,))
            conn.commit()
            flash('Blog post and associated likes deleted.')

        return redirect(url_for('dashboard'))

    cursor.execute("SELECT * FROM blogs WHERE username = %s", (session['username'],))
    blogs = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('dashboard.html', blogs=blogs)

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if 'username' not in session or not session.get('is_admin'):
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            if 'delete_user' in request.form:
                user_id = request.form['username']
                cursor.execute("SELECT blog_id FROM blog_likes WHERE user_id = %s", (user_id,))
                delul=cursor.fetchall()
                cursor.execute("DELETE FROM blog_likes WHERE user_id = %s", (user_id,))
                for i in delul:
                    cursor.execute("UPDATE blogs set like_count=like_count-1 where id=%s",i)
                cursor.execute("select username from users where id=%s", (user_id,))
                username=cursor.fetchone()
                cursor.execute("DELETE FROM blogs WHERE username = %s", username)
                cursor.execute("DELETE FROM users WHERE username = %s", username)
                conn.commit()
                flash(f'User {user_id} deleted.')

            if 'make_admin' in request.form:
                user_id = request.form['username']
                cursor.execute("Select is_admin from users where id=%s", (user_id,))
                for i in cursor.fetchone():
                    sisadmin=i
                if sisadmin == 1:
                    flash("User is already admin")
                else:
                    cursor.execute("UPDATE users SET is_admin = TRUE WHERE id = %s", (user_id,))
                    flash('User promoted to admin.')
                conn.commit()

            if 'remove_admin' in request.form:
                user_id = request.form['username']
                cursor.execute("UPDATE users SET is_admin = FALSE WHERE id = %s", (user_id,))
                conn.commit()
                flash('Admin demoted to user.')
        except KeyError:
            flash("no user selected")

        try:
            if 'delete_blog' in request.form:
                blog_id = request.form['blog']

                # Delete likes associated with the blog first
                cursor.execute("DELETE FROM blog_likes WHERE blog_id = %s", (blog_id,))

                # Now delete the blog
                cursor.execute("DELETE FROM blogs WHERE id = %s", (blog_id,))
                conn.commit()
                flash('Blog post and associated likes deleted.')
        except KeyError:
            flash("no blog selected")
        return redirect(url_for('admin'))

    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT id, title FROM blogs")
    blogs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin.html', users=users, blogs=blogs)

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('username', None)  # Clear the session
    session.pop('is_admin', None)   # Clear admin status from session
    flash('You have been logged out successfully.')  # Optional: Flash a logout success message
    return redirect(url_for('login'))

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(directory=os.path.join(app.root_path, 'templates'), path='sitemap.xml', mimetype='application/xml')

@app.route('/robots.txt')
def robots_txt():
    return send_from_directory(directory=os.path.join(app.root_path, 'static'), path='robots.txt', mimetype='text/plain')
@app.route('/author-aman')
def author_aman():
    # You can pass any necessary data to the template
    return render_template('author-aman.html')

if __name__ == '__main__':
    app.run(debug=True, port=2000)