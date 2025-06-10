from flask import Blueprint, render_template, request, redirect, session, flash
from flask_bcrypt import Bcrypt
from app.models import db, cursor

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        cursor.execute("SELECT id, password, is_admin FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            cursor.execute("INSERT INTO users (username, email, password, role, is_admin) VALUES (%s, %s, %s, 'user', %s)",
                       (username, email, password, False))
            flash('Registration was Successful!', 'success')
        else:
            flash('Email is already registered pls login!', 'error')
            return redirect('/register')
        db.commit()
        return redirect('/login')

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT id, password, is_admin FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['is_admin'] = user[2]
            flash('Login was Successful!', 'success')
            return redirect('/admin' if user[2] else '/')
        else:
            flash('Login was Unsuccessful! Please check if username or password is correct', 'error')
            return redirect('/login')

    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash('Logout was Successful!', 'success')
    return redirect('/login')
