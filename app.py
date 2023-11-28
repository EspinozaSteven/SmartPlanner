from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

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
        db.execute("INSERT INTO tbl_user (user_name,user_email, user_password,created_at) VALUES (:username, :email, :hash,:createddate);", username=username,email=mail, hash=hash,createddate=datetime.now())
        # Creating the new workspace 
        row = db.execute("SELECT id FROM tbl_user WHERE user_name = ?;", username)
        db.execute("INSERT INTO tbl_work_space (title,topic,isPersonal,owner,description,state_id,created_at) VALUES (:title, :topic, :isPersonal, :owner, :description, :state_id, :created_at);", title="Espacio personal",topic="Primer espacio",description="Puedes crear ahora tareas, anotaciones o recordatorios", isPersonal=1,owner =row[0]["id"], state_id="1", created_at=datetime.now())
        
        # redirecting to login page
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Forget any user_id
    session.clear()
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
                session["user_id"] = row[0]["id"]
                session["user_name"] = row[0]["user_name"]
                session["user_email"] = row[0]["user_email"]
                if row[0]["user_photo"]:
                    session["user_photo"] = row[0]["user_photo"]
                return home()
        return render_template('login.html', error='Incorrect credentials')
    return render_template('login.html', error=error)

@app.route('/home', methods=['GET', 'POST'])
def home():
    row = db.execute("SELECT * FROM tbl_work_space as a WHERE a.owner=? AND a.isPersonal=1;",session["user_id"])
    work_space = []
    work_space.append({"id":row[0]["id"],"title":row[0]["title"],"topic":row[0]["topic"],"description":row[0]["description"]})
    return render_template('home.html',work_space=work_space)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/note", methods=['GET', 'POST'])
def note():
    if request.method == 'POST':
        work_space_id = request.form['work_space_id']
        title = request.form['title']
        description = request.form['description']
        if not title:
            return render_template('home.html', error='Title is required')
        if not description:
            return render_template('home.html', error='Description is required')
        if not work_space_id:
            return render_template('home.html', error='Work_space_id is required')
        db.execute("INSERT INTO tbl_note (work_space_id,title,description,state_id,created_at) VALUES (?,?,?,?,?);",work_space_id,title,description,1,datetime.now())
        return redirect("home")

@app.route("/reminder", methods=['GET', 'POST'])
def reminder():
    if request.method == 'POST':
        work_space_id = request.form['work_space_id']
        title = request.form['title']
        description = request.form['description']
        reminder_date=request.form['reminder_date']
        if not title:
            return render_template('home.html', error='Title is required')
        if not description:
            return render_template('home.html', error='Description is required')
        if not reminder_date:
            return render_template('home.html', error='Reminder date is required')
        if not work_space_id:
            return render_template('home.html', error='Work_space_id is required')
        db.execute("INSERT INTO tbl_reminder (work_space_id,title,description,reminder_date,state_id,created_at) VALUES (?,?,?,?,?,?);",work_space_id,title,description,reminder_date,1,datetime.now())
        return redirect("home")
    
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)