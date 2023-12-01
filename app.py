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
UPLOAD_FOLDER = 'static/uploads'
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
            return render_template('workspace.html', error='Title is required')
        if not topic:
            return render_template('workspace.html', error='Topic is required')
        if not description:
            return render_template('workspace.html', error='Description is required')
        db.execute("INSERT INTO tbl_work_space (title,topic,isPersonal,owner,description,state_id,created_at) VALUES (?,?,?,?,?,?,?);",title,topic,0,session['user_id'],description,1,datetime.now())
        # Ingresar miembro
        work_space_id = db.execute("SELECT id FROM tbl_work_space WHERE owner = ? ORDER BY created_at DESC LIMIT 1;", session["user_id"])[0]["id"]
        db.execute("INSERT INTO tbl_work_space_member (work_space_id,user_id,created_at) VALUES (?,?,?);", work_space_id, session["user_id"], datetime.now())
        return render_template('workspace.html', success='Se ha creado el espacio de trabajo '+title)

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
    
    row = db.execute("SELECT a.*,b.name FROM tbl_reminder as a INNER JOIN cat_state as b on (b.id=a.state_id) WHERE a.work_space_id=? ORDER BY a.reminder_date ASC;",id)
    
    reminders=[]
    for item in row:
        reminders.append({"id":item["id"],"title":item["title"],"description":item["description"],"reminder_date":item["reminder_date"],"state_id":item["state_id"],"state_name":item["name"]})

    row = db.execute("SELECT a.*,b.name FROM tbl_task as a INNER JOIN cat_state as b on (b.id=a.state_id) WHERE a.work_space_id=? ORDER BY a.expired_date ASC;",id)

    tasks=[]
    for item in row:
        tasks.append({"id":item["id"],"title":item["title"],"description":item["description"],"expired_date":item["expired_date"],"state_id":item["state_id"],"state_name":item["name"]})

    return render_template('workspace.html',work_space=data,notes=notes,reminders=reminders,task=tasks)

@app.route('/workspace/<int:id>/members', methods=['GET','POST'])
def work_space_members(id):
    if request.method == 'POST':
        errores=[]
        member_count = request.form['contador']
        if int(member_count)>0:
            for i in range(1,(int(member_count)+1)):
                try:
                    miembro = request.form['miembro'+str(i)]
                    if miembro:
                        #Validar que el correo pertenezca a un usuario
                        row = db.execute("SELECT a.id FROM tbl_user as a WHERE a.user_email=?;",miembro)
                        if len(row)>0:
                            #Validar que no te estes invitando a ti mismo
                            if miembro == session['user_email']:
                                errores.append("El email: "+miembro+" te pertenece a ti. No puedes invitarte a ti mismo")
                                continue
                            #Validar que el usuario no halla sido invitado ya
                            row2 = db.execute("SELECT a.id FROM tbl_work_space_member_invitation as a WHERE a.work_space_id=? AND user_id=?;",id,row[0]['id'])
                            if len(row2)>0:
                                errores.append("El usuario con email: "+miembro+" ya esta en el grupo")
                                continue
                            #Validar que este usaurio no pertenezca ya al grupo de trabajo
                            row3 = db.execute("SELECT a.id FROM tbl_work_space_member as a WHERE a.work_space_id=? AND user_id=?;",id,row[0]['id'])
                            if len(row3)>0:
                                errores.append("El usuario con email: "+miembro+" ya esta en el grupo")
                                continue
                            db.execute("INSERT INTO tbl_work_space_member_invitation (work_space_id,user_id,state_id,created_by,created_at) VALUES (?,?,?,?,?);",id,row[0]['id'],1,session['user_id'],datetime.now())
                        else:
                            errores.append("El correo: "+miembro+" no pertenece a ningun usuario registrado. No se agrego el miembro")
                            continue
                except KeyError:
                    errores.append("El miembro "+str(i)+" no fue definido")

        work_space = db.execute("SELECT a.* FROM tbl_work_space as a WHERE a.id=?;",id)
        members = db.execute("SELECT a.*,b.user_name FROM tbl_work_space_member as a INNER JOIN tbl_user as b on (b.id=user_id) WHERE a.work_space_id=?;",id)
        return render_template("members.html",work_space=work_space,members=members,errores=errores)
        #return redirect(url_for('work_space_members', id=id))

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
        user_name = request.form['user_name']
        current_password = request.form['current_password']
        new_password = request.form['new_password'] 
        repeat_password = request.form['repeat_password']

        if not user_name:
            return render_template('configuracion.html', error='The field user name is required')
        
        if not current_password:
            return render_template('configuracion.html', error='The field current password is required')
        
        row = db.execute("SELECT user_password FROM tbl_user WHERE user_name = ?", session['user_name'])
        if row:
            if not (check_password_hash(row[0]["user_password"],current_password)):
                return render_template('configuracion.html', error='La contraseña es incorrecta')
            
        db.execute('UPDATE tbl_user SET user_name = ? WHERE id = ?;', user_name,session['user_id'])
        session['user_name']=user_name
        
        if new_password:
            if not repeat_password:
                return render_template('configuracion.html', error='The field repeat password is required')
            else:
                if not(repeat_password == new_password):
                    return render_template('configuracion.html', error='Las contraseñas deben ser iguales')
                # Actualiza la contraseña del usuario
                db.execute('UPDATE tbl_user SET user_password = ? WHERE id = ?;', generate_password_hash(new_password),session['user_id'])
            

        if 'user_img' in request.files:
            archivo = request.files['user_img']

            if not(archivo.filename == ''):
                if archivo:
                    if not os.path.exists(app.config['UPLOAD_FOLDER']):
                        os.makedirs(app.config['UPLOAD_FOLDER'])
                    #Obtener y borrar la imagen actual del usuario, antes de guardar la nueva
                    #Obtener la ruta de la imagen desde la base de datos
                    ruta = db.execute("SELECT a.user_photo FROM tbl_user as a WHERE a.id = ?;",session['user_id'])
                    if (len(ruta)>0) and (ruta[0]['user_photo'] is not None):
                        ruta=ruta[0]['user_photo']
                        # Comprobar si la imagen existe antes de intentar borrarla
                        if os.path.exists(ruta):
                            os.remove(ruta)
                    
                    #Guardar la nueva imagen
                    ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
                    archivo.save(ruta_archivo)

                    # Guarda la ruta en la base de datos
                    db.execute('UPDATE tbl_user SET user_photo = ? WHERE id = ?;', ruta_archivo,session['user_id'])
                    session['user_photo']=ruta_archivo

                    return render_template("configuracion.html",success="Se han guardado las configuraciones")
    return render_template("configuracion.html")

@app.route("/note", methods=['GET', 'POST'])
def note():
    if request.method == 'POST':
        work_space_id = request.form['work_space_id']
        title = request.form['title']
        description = request.form['description']
        if not title:
            return render_template("workspace/"+str(work_space_id),error="Title is required")
        if not description:
            return render_template("workspace/"+str(work_space_id),error="Description is required")
        if not work_space_id:
            return render_template("workspace/"+str(work_space_id),error="Work space id is required")
        db.execute("INSERT INTO tbl_note (work_space_id,title,description,state_id,created_at) VALUES (?,?,?,?,?);",work_space_id,title,description,1,datetime.now())
        return render_template("workspace/"+str(work_space_id),success="Se ha agregado la nota")

@app.route("/reminder", methods=['GET', 'POST'])
def reminder():
    if request.method == 'POST':
        work_space_id = request.form['work_space_id']
        title = request.form['title']
        description = request.form['description']
        reminder_date=request.form['reminder_date']
        if not title:
            return render_template("workspace/"+str(work_space_id),error="Title is required")
        if not description:
            return render_template("workspace/"+str(work_space_id),error="Description is required")
        if not reminder_date:
            return render_template("workspace/"+str(work_space_id),error="Reminder date is required")
        if not work_space_id:
            return render_template("workspace/"+str(work_space_id),error="Work_space_id date is required")
        
        try:
            reminder_date = datetime.strptime(reminder_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            return render_template("workspace/"+str(work_space_id),error="El formato de fecha especificado es invalido")

        if reminder_date <= datetime.now():
            return render_template("workspace/"+str(work_space_id),error="La fecha no es valida")
        
        db.execute("INSERT INTO tbl_reminder (work_space_id,title,description,reminder_date,state_id,created_at) VALUES (?,?,?,?,?,?);",work_space_id,title,description,reminder_date,1,datetime.now())
        return render_template("workspace/"+str(work_space_id),success="Se ha agregado el recordatorio")
    
@app.route("/task", methods=['GET', 'POST'])
def task():
    if request.method == 'POST':
        work_space_id = request.form['work_space_id']
        title = request.form['title']
        description = request.form['description']
        expired_date=request.form['expired_date']
        activity_count = request.form['act'];

        if not title:
            return render_template("workspace/"+str(work_space_id),error="Title is required")
        if not description:
            return render_template("workspace/"+str(work_space_id),error="Description is required")
        if not expired_date:
            return render_template("workspace/"+str(work_space_id),error="Expired date is required")
        if not work_space_id:
            return render_template("workspace/"+str(work_space_id),error="Work_space_id is required")
        if not activity_count:
            return render_template("workspace/"+str(work_space_id),error="Activity count is required")
        
        if int(activity_count)<1:
            return render_template("workspace/"+str(work_space_id),error="Is requiered almost one activity")

        try:
            expired_date = datetime.strptime(expired_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            return render_template("workspace/"+str(work_space_id),error="Formato de fecha invalido")

        if expired_date <= datetime.now():
            return render_template("workspace/"+str(work_space_id),error="La fecha es invaldia")
        
        db.execute("INSERT INTO tbl_task (work_space_id,title,description,expired_date,state_id,created_by,created_at) VALUES (?,?,?,?,?,?,?);",work_space_id,title,description,expired_date,1,session['user_id'],datetime.now())
        
        activity_id = db.execute("SELECT id FROM tbl_task WHERE created_by = ? ORDER BY created_at DESC LIMIT 1;", session["user_id"])[0]["id"]

        # Insertando actividades
        for i in range(1,(int(activity_count)+1)):
            try:
                actividad = request.form['actividad'+str(i)]
                # Continuar con el resto de tu código
                if actividad:
                    db.execute("INSERT INTO tbl_task_activity (task_id,activity,state_id,created_at) VALUES (?,?,?,?);",activity_id,actividad,1,datetime.now())
            except KeyError:
                print("No viene la actividad")

        return render_template("workspace/"+str(work_space_id),success="Tarea agregada con exito")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)