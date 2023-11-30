from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configura la carpeta donde se guardarán las imágenes
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        # Ingresar miembro
        work_space_id = db.execute("SELECT id FROM tbl_work_space WHERE owner = ? AND isPersonal=1;", row[0]["id"])[0]["id"]
        db.execute("INSERT INTO tbl_work_space_member (work_space_id,user_id,created_at) VALUES (?,?,?);", work_space_id, row[0]["id"], datetime.now())
        
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
                return redirect("/home")
        return render_template('login.html', error='Incorrect credentials')
    return render_template('login.html', error=error)

@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session.get("user_id"):
        return redirect(url_for('login'))
    rows = db.execute("SELECT * FROM tbl_work_space as a WHERE a.owner=?;",session["user_id"])
    work_spaces = []
    for row in rows:
        work_spaces.append({"id":row["id"],"title":row["title"],"topic":row["topic"],"description":row["description"]})
    session["work_spaces"] = work_spaces
    return render_template('home.html',work_spaces=work_spaces)

@app.route("/workspace", methods=['POST'])
def workspace():
    if request.method == 'POST':
        title = request.form['title']
        topic = request.form['topic']
        description=request.form['description']
        if not title:
            return render_template('home.html', error='Title is required')
        if not topic:
            return render_template('home.html', error='Topic is required')
        if not description:
            return render_template('home.html', error='Description is required')
        db.execute("INSERT INTO tbl_work_space (title,topic,isPersonal,owner,description,state_id,created_at) VALUES (?,?,?,?,?,?,?);",title,topic,0,session['user_id'],description,1,datetime.now())
        # Ingresar miembro
        work_space_id = db.execute("SELECT id FROM tbl_work_space WHERE owner = ? ORDER BY created_at DESC LIMIT 1;", session["user_id"])[0]["id"]
        db.execute("INSERT INTO tbl_work_space_member (work_space_id,user_id,created_at) VALUES (?,?,?);", work_space_id, session["user_id"], datetime.now())
        return redirect("home")

@app.route('/workspace/<int:id>', methods=['GET'])
def work_space(id):
    # Showing work spaces
    if not session.get("user_id"):
        return redirect(url_for('login'))
    data = db.execute("SELECT * FROM tbl_work_space as a WHERE id=?;",id)
    
    row = db.execute("SELECT a.*,b.name FROM tbl_note as a INNER JOIN cat_state as b on (b.id=a.state_id) WHERE a.work_space_id=? ORDER BY a.created_at DESC;",id)
    
    notes=[]
    for item in row:
        notes.append({"id":item["id"],"title":item["title"],"description":item["description"],"state_id":item["state_id"],"state_name":item["name"]})
    
    row = db.execute("SELECT a.*,b.name FROM tbl_reminder as a INNER JOIN cat_state as b on (b.id=a.state_id) WHERE a.work_space_id=? ORDER BY a.created_at ASC;",id)
    
    reminders=[]
    for item in row:
        reminders.append({"id":item["id"],"title":item["title"],"description":item["description"],"reminder_date":item["reminder_date"],"state_id":item["state_id"],"state_name":item["name"]})

    row = db.execute("SELECT a.*,b.name FROM tbl_task as a INNER JOIN cat_state as b on (b.id=a.state_id) WHERE a.work_space_id=? ORDER BY a.created_at ASC;",id)

    tasks=[]
    for item in row:
        tasks.append({"id":item["id"],"title":item["title"],"description":item["description"],"expired_date":item["expired_date"],"state_id":item["state_id"],"state_name":item["name"]})

    return render_template('workspace.html',work_space=data,notes=notes,reminders=reminders,task=tasks)

@app.route('/workspace/<int:id>/members', methods=['GET','POST'])
def work_space_members(id):
    if request.method == 'POST':
        member_count = request.form['contador']#miembro1
        if member_count>0:
            return redirect("register")
        
        user_email = request.form['title']
        description = request.form['description']

    work_space = db.execute("SELECT a.* FROM tbl_work_space as a WHERE a.id=?;",id)
    members = db.execute("SELECT a.*,b.user_name FROM tbl_work_space_member as a INNER JOIN tbl_user as b on (b.id=user_id) WHERE a.work_space_id=?;",id)
    return render_template("members.html",work_space=work_space,members=members)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/configuracion",methods=['GET','POST'])
def configuracion():
    if request.method == 'POST':
        if 'user_img' not in request.files:
            return 'No se ha seleccionado ningún archivo'

        archivo = request.files['user_img']

        if archivo.filename == '':
            return 'Nombre de archivo no válido'

        if archivo:
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
            archivo.save(ruta_archivo)

            # Guarda la ruta en la base de datos
            db.execute('UPDATE tbl_user SET user_photo = ? WHERE id = ?;', ruta_archivo,session['user_id'])

            return 'Imagen subida con éxito y ruta guardada en la base de datos'
    return render_template("configuracion.html")

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
            return redirect("/home")
        db.execute("INSERT INTO tbl_note (work_space_id,title,description,state_id,created_at) VALUES (?,?,?,?,?);",work_space_id,title,description,1,datetime.now())
        return redirect("workspace/"+str(work_space_id))

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
        
        try:
            reminder_date = datetime.strptime(reminder_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            return redirect('/register')

        if reminder_date <= datetime.now():
            return redirect('/login')
        
        db.execute("INSERT INTO tbl_reminder (work_space_id,title,description,reminder_date,state_id,created_at) VALUES (?,?,?,?,?,?);",work_space_id,title,description,reminder_date,1,datetime.now())
        return redirect("workspace/"+str(work_space_id))
    
@app.route("/task", methods=['GET', 'POST'])
def task():
    if request.method == 'POST':
        work_space_id = request.form['work_space_id']
        title = request.form['title']
        description = request.form['description']
        expired_date=request.form['expired_date']
        if not title:
            return render_template('home.html', error='Title is required')
        if not description:
            return render_template('home.html', error='Description is required')
        if not expired_date:
            return render_template('home.html', error='Expired date is required')
        if not work_space_id:
            return render_template('home.html', error='Work_space_id is required')
        
        try:
            expired_date = datetime.strptime(expired_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            return redirect('/register')

        if expired_date <= datetime.now():
            return redirect('/login')
        
        db.execute("INSERT INTO tbl_task (work_space_id,title,description,expired_date,state_id,created_at) VALUES (?,?,?,?,?,?);",work_space_id,title,description,expired_date,1,datetime.now())
        return redirect("workspace/"+str(work_space_id))

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)