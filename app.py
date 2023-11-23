from flask import Flask, render_template, request, redirect, url_for, flash
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# Database config
db = SQL("sqlite:///SmartPlanner.db")

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # validating data
        mail = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirmpass = request.form['confirmation']
        if not username:
            return render_template('register.html', error='Username is required')
        elif not mail:
            return render_template('register.html', error='Email is required')
        elif not password:
            return render_template('register.html', error='Password is required')
        elif not confirmpass:
            return render_template('register.html', error='Confirm password is required')
        elif password != confirmpass:
            return render_template('register.html', error='Password and Confirm password do not match')
        elif db.execute("SELECT * FROM tbl_user WHERE user_name = :username", username=username):
            return render_template('register.html', error='Username already exists')
        # encrypting password
        hash = generate_password_hash(password)
        # inserting data into database
        db.execute("INSERT INTO tbl_user (user_name,user_email, user_password,created_at) VALUES (:username, :email, :hash,:createddate)", username=username,email=mail, hash=hash,createddate=datetime.now())
        # redirecting to login page
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
         # validating data
        username = request.form['username']
        password = request.form['password']
        if not username:
            return render_template('login.html', error='Username is required')
        elif not password:
            return render_template('login.html', error='Password is required')
        row = db.execute("SELECT * FROM tbl_user WHERE user_name = :username", username=username)
        if row:
            # validating pass
            if check_password_hash(row[0]["user_password"],password):
                userData={"username":row[0]["user_name"],"id":row[0]["id"]}
                return render_template('home.html',userData=userData)
        return render_template('login.html', error='Incorrect credentials')
        
        return redirect(url_for('login'))
    return render_template('login.html', error=error)

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')