from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management


def create_user_table():
    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        connection.commit()
        print("User table created successfully.")
    except Error as e:
        print(f"Error: {e}")


def add_user(username, password):
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        connection.commit()
        print(f"User {username} added successfully.")
    except Error as e:
        print(f"Error: {e}")


def get_user(username, password):
    users = []
    try:
        cursor = connection.cursor()

        # vulnerable query (e.g. when username is `aaa' OR '1=1` and password is `aaa' OR '1=1`)
        cursor.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")

        # secure query
        # cursor.execute(f"SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        users = cursor.fetchall()
    except Error as e:
        print(f"Error: {e}")
    return users


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        add_user(username, password)
        flash(f"User {username} registered successfully!", 'success')
        return render_template('index.html')
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = get_user(username, password)

        if users:
            for user in users:
                session['user_id'] = user[0]  # Store user ID in the session
                flash(f"Welcome back, {user[1]}!", 'success')
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password. Please try again.", 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear the user ID from the session
    flash("You have been logged out.", 'info')
    return redirect(url_for('home'))


if __name__ == '__main__':

    connection = sqlite3.connect('site.db', check_same_thread=False)
    print("Connection to SQLite DB successful.")
    create_user_table()

    app.run(host='0.0.0.0', port=8080)
