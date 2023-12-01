from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from flask_mail import Mail, Message

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configura la carpeta donde se guardarán las imágenes
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configuración para Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Cambia esto al servidor de correo saliente que estés utilizando
app.config['MAIL_PORT'] = 587  # Puerto para el servidor de correo saliente
app.config['MAIL_USE_TLS'] = True  # Usar TLS (SSL se usa si MAIL_USE_TLS es False)
app.config['MAIL_USE_SSL'] = False  # Usar SSL (si MAIL_USE_TLS es False)
app.config['MAIL_USERNAME'] = 'espinozasteven1002@gmail.com'  # Tu dirección de correo electrónico
app.config['MAIL_PASSWORD'] = 'qgwa botr rxon kclh'  # Tu contraseña de correo electrónico

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database config
db = SQL("sqlite:///SmartPlanner.db")
mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

def sendMain(destino,espacio):
    # Crear el mensaje de correo
    subject = 'Invitación de SmartPlanner'
    sender = session['user_email']
    recipients = [destino]
    body = 'Has sido invitado por '+sender+ ' ha unirte al espacio de trabajo "'+espacio+'"'
    msg = Message(subject=subject, sender=sender, recipients=recipients, body=body)

    # Enviar el correo electrónico
    mail.send(msg)

    return True

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
                session["success"] = []
                session["errors"] = []
                return redirect("/home")
        return render_template('login.html', error='Incorrect credentials')
    return render_template('login.html', error=error)

@app.route('/home', methods=['GET'])
def home():
    if not session.get("user_id"):
        return redirect(url_for('login'))
    rows = db.execute("SELECT * FROM tbl_work_space as a WHERE a.owner=?;",session["user_id"])
    work_spaces = []
    for row in rows:
        work_spaces.append({"id":row["id"],"title":row["title"],"topic":row["topic"],"description":row["description"]})
    session["work_spaces"] = work_spaces
    success = session['success']
    errors = session['errors']
    session['success']=[]
    session['errors']=[]
    return render_template('home.html',work_spaces=work_spaces,success=success,errors=errors)

@app.route("/workspace", methods=['POST'])
def workspace():
    if request.method == 'POST':
        title = request.form['title']
        topic = request.form['topic']
        description=request.form['description']
        if not title:
            session["errors"].append("Title is required")
            return redirect('home')
        if not topic:
            session["errors"].append("Topic is required")
            return redirect('home')
        if not description:
            session["errors"].append("Description is required")
            return redirect('home')
        db.execute("INSERT INTO tbl_work_space (title,topic,isPersonal,owner,description,state_id,created_at) VALUES (?,?,?,?,?,?,?);",title,topic,0,session['user_id'],description,1,datetime.now())
        # Ingresar miembro
        work_space_id = db.execute("SELECT id FROM tbl_work_space WHERE owner = ? ORDER BY created_at DESC LIMIT 1;", session["user_id"])[0]["id"]
        db.execute("INSERT INTO tbl_work_space_member (work_space_id,user_id,created_at) VALUES (?,?,?);", work_space_id, session["user_id"], datetime.now())
        session["success"].append("Se ha creado el espacio de trabajo "+title)
        return redirect('home')

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

    success = session['success']
    errors = session['errors']
    session['success']=[]
    session['errors']=[]
    return render_template('workspace.html',work_space=data,notes=notes,reminders=reminders,task=tasks,success=success,errors=errors)

@app.route('/workspace/<int:id>/members', methods=['GET','POST'])
def work_space_members(id):
    if request.method == 'POST':
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
                                session["errors"].append("El email: "+miembro+" te pertenece a ti. No puedes invitarte a ti mismo")
                                continue
                            #Validar que el usuario no halla sido invitado ya
                            row2 = db.execute("SELECT a.id FROM tbl_work_space_member_invitation as a WHERE a.work_space_id=? AND user_id=?;",id,row[0]['id'])
                            if len(row2)>0:
                                session["errors"].append("El usuario con email: "+miembro+" ya ha sido invitado a este grupo")
                                continue
                            #Validar que este usaurio no pertenezca ya al grupo de trabajo
                            row3 = db.execute("SELECT a.id FROM tbl_work_space_member as a WHERE a.work_space_id=? AND user_id=?;",id,row[0]['id'])
                            if len(row3)>0:
                                session["errors"].append("El usuario con email: "+miembro+" ya esta en el grupo")
                                continue
                            db.execute("INSERT INTO tbl_work_space_member_invitation (work_space_id,user_id,state_id,created_by,created_at) VALUES (?,?,?,?,?);",id,row[0]['id'],1,session['user_id'],datetime.now())
                            
                            #Envio de correo
                            #ws = db.execute("SELECT a.* FROM tbl_work_space as a WHERE a.id=?;",id)
                            #sendMain(miembro,ws[0]['title'])

                            session["success"].append("El usuario con email: "+miembro+" ha sido invitado al espacio de trabajo")
                        else:
                            session["errors"].append("El correo: "+miembro+" no pertenece a ningun usuario registrado. No se agrego el miembro")
                            continue
                except KeyError:
                    session["errors"].append("El miembro "+str(i)+" no fue definido")
        return redirect(url_for('work_space_members', id=id))

    work_space = db.execute("SELECT a.* FROM tbl_work_space as a WHERE a.id=?;",id)
    members = db.execute("SELECT a.*,b.user_name FROM tbl_work_space_member as a INNER JOIN tbl_user as b on (b.id=user_id) WHERE a.work_space_id=?;",id)
    success = session['success']
    errors = session['errors']
    session['success']=[]
    session['errors']=[]
    return render_template("members.html",work_space=work_space,members=members,success=success,errors=errors)

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
            session["errors"].append("The field user name is required")
            return redirect('configuracion')
        
        if not current_password:
            session["errors"].append("The field current password is required")
            return redirect('configuracion')
        
        row = db.execute("SELECT user_password FROM tbl_user WHERE user_name = ?", session['user_name'])
        if row:
            if not (check_password_hash(row[0]["user_password"],current_password)):
                session["errors"].append("La contraseña es incorrecta")
                return redirect('configuracion')
            
        db.execute('UPDATE tbl_user SET user_name = ? WHERE id = ?;', user_name,session['user_id'])
        session['user_name']=user_name
        
        if new_password:
            if not repeat_password:
                return render_template('configuracion.html', error='The field repeat password is required')
            else:
                if not(repeat_password == new_password):
                    session["errors"].append("Las contraseñas deben ser iguales")
                    return redirect('configuracion')
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
                    session["success"].append("Se han guardado las configuraciones")
                    return redirect("configuracion")
        session["success"].append("Se han guardado las configuraciones")
        return redirect("configuracion")
    success = session['success']
    errors = session['errors']
    session['success']=[]
    session['errors']=[]
    return render_template("configuracion.html",success=success,errors=errors)

@app.route("/note", methods=['POST'])
def note():
    if request.method == 'POST':
        work_space_id = request.form['work_space_id']
        title = request.form['title']
        description = request.form['description']
        if not title:
            session["errors"].append("Title is required")
            return redirect("workspace/"+str(work_space_id))
        if not description:
            session["errors"].append("Description is required")
            return redirect("workspace/"+str(work_space_id))
        if not work_space_id:
            session["errors"].append("Work space id is required")
            return redirect("workspace/"+str(work_space_id))
        db.execute("INSERT INTO tbl_note (work_space_id,title,description,state_id,created_at) VALUES (?,?,?,?,?);",work_space_id,title,description,1,datetime.now())
        session["success"].append("La nota se ha agregado")
        return redirect("workspace/"+str(work_space_id))

@app.route("/reminder", methods=['GET', 'POST'])
def reminder():
    if request.method == 'POST':
        work_space_id = request.form['work_space_id']
        title = request.form['title']
        description = request.form['description']
        reminder_date=request.form['reminder_date']
        if not title:
            session["errors"].append("Title is required")
            return redirect("workspace/"+str(work_space_id))
        if not description:
            session["errors"].append("Description is required")
            return redirect("workspace/"+str(work_space_id))
        if not reminder_date:
            session["errors"].append("Reminder date is required")
            return redirect("workspace/"+str(work_space_id))
        if not work_space_id:
            session["errors"].append("Work_space_id date is required")
            return redirect("workspace/"+str(work_space_id))
        
        try:
            reminder_date = datetime.strptime(reminder_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            session["errors"].append("El formato de fecha especificado es invalido")
            return redirect("workspace/"+str(work_space_id))

        if reminder_date <= datetime.now():
            session["errors"].append("La fecha no es valida")
            return redirect("workspace/"+str(work_space_id))
        
        db.execute("INSERT INTO tbl_reminder (work_space_id,title,description,reminder_date,state_id,created_at) VALUES (?,?,?,?,?,?);",work_space_id,title,description,reminder_date,1,datetime.now())
        session["success"].append("Se ha agregado el recordatorio")
        return redirect("workspace/"+str(work_space_id))
    
@app.route("/task", methods=['GET', 'POST'])
def task():
    if request.method == 'POST':
        work_space_id = request.form['work_space_id']
        title = request.form['title']
        description = request.form['description']
        expired_date=request.form['expired_date']
        activity_count = request.form['act'];

        if not title:
            session["errors"].append("El titulo es requerido")
            return redirect("workspace/"+str(work_space_id))
        if not description:
            session["errors"].append("La descripción es requerida")
            return redirect("workspace/"+str(work_space_id))
        if not expired_date:
            session["errors"].append("La fecha de expiración es requerida")
            return redirect("workspace/"+str(work_space_id))
        if not work_space_id:
            session["errors"].append("El id del espacio de trabajo es requerido")
            return redirect("workspace/"+str(work_space_id))
        if not activity_count:
            session["errors"].append("La cantidad de actividades es requerida")
            return redirect("workspace/"+str(work_space_id))
        
        if int(activity_count)<1:
            session["errors"].append("Es requerido ingresar almenos una actividad")
            return redirect("workspace/"+str(work_space_id))

        try:
            expired_date = datetime.strptime(expired_date, '%Y-%m-%dT%H:%M')
        except ValueError:
            session["errors"].append("El formato de la fecha no es valido")
            return redirect("workspace/"+str(work_space_id))

        if expired_date <= datetime.now():
            session["errors"].append("La fecha no es valida")
            return redirect("workspace/"+str(work_space_id))
        
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
        session["success"].append("Tarea agregada con exito")
        return redirect("workspace/"+str(work_space_id))

@app.route("/notas", methods=['GET'])
def notas():
    # Showing work spaces
    if not session.get("user_id"):
        return redirect(url_for('login'))
    
    work_spaces = db.execute("SELECT b.title,b.id FROM tbl_work_space_member as a INNER JOIN tbl_work_space as b on (b.id=a.work_space_id) WHERE a.user_id=?;",session['user_id'])
    notas = []

    for index, item in enumerate(work_spaces):
        contador = 0
        search_notes=db.execute("SELECT a.*,b.name FROM tbl_note as a INNER JOIN cat_state as b on (b.id=a.state_id) WHERE a.work_space_id=?;",item['id'])
        for item2 in search_notes:
            notas.append({"work_space":item['title'],"id":item2["id"],"title":item2["title"],"description":item2["description"],"state_id":item2["state_id"],"state_name":item2["name"]})
            contador+=1
        if contador<=0:
            work_spaces[index]["Tiene"] = "No" 
    return render_template('notas.html',notes=notas,work_spaces=work_spaces)

@app.route("/recordatorios", methods=['GET'])
def recordatorios():
    # Showing work spaces
    if not session.get("user_id"):
        return redirect(url_for('login'))
    
    work_spaces = db.execute("SELECT b.title,b.id FROM tbl_work_space_member as a INNER JOIN tbl_work_space as b on (b.id=a.work_space_id) WHERE a.user_id=?;",session['user_id'])
    reminders = []

    for index, item in enumerate(work_spaces):
        contador = 0
        search_reminders=db.execute("SELECT a.*,b.name FROM tbl_reminder as a INNER JOIN cat_state as b on (b.id=a.state_id) WHERE a.work_space_id=? ORDER BY a.reminder_date ASC;",item['id'])
        for item2 in search_reminders:
            reminders.append({"work_space":item['title'],"id":item2["id"],"title":item2["title"],"description":item2["description"],"reminder_date":item2["reminder_date"],"state_id":item2["state_id"],"state_name":item2["name"]})
            contador+=1
        if contador<=0:
            work_spaces[index]["Tiene"] = "No" 
    return render_template('recordatorios.html',reminders=reminders,work_spaces=work_spaces)

@app.route("/tareas", methods=['GET'])
def tareas():
    # Showing work spaces
    if not session.get("user_id"):
        return redirect(url_for('login'))
    
    work_spaces = db.execute("SELECT b.title,b.id FROM tbl_work_space_member as a INNER JOIN tbl_work_space as b on (b.id=a.work_space_id) WHERE a.user_id=?;",session['user_id'])
    tasks = []

    for index, item in enumerate(work_spaces):
        contador = 0
        search_tasks=db.execute("SELECT a.*,b.name FROM tbl_task as a INNER JOIN cat_state as b on (b.id=a.state_id) WHERE a.work_space_id=? ORDER BY a.expired_date ASC;",item['id'])
        for item2 in search_tasks:
            tasks.append({"work_space":item['title'],"id":item2["id"],"title":item2["title"],"description":item2["description"],"expired_date":item2["expired_date"],"state_id":item2["state_id"],"state_name":item2["name"]})
            contador+=1
        if contador<=0:
            work_spaces[index]["Tiene"] = "No" 
    return render_template('tareas.html',tasks=tasks,work_spaces=work_spaces)

@app.route("/tarea/<int:id>", methods=['GET'])
def notas(id):
    # Showing work spaces
    if not session.get("user_id"):
        return redirect(url_for('login'))
    
    nota = db.execute("SELECT a.*, b.name FROM tbl_note as a INNER JOIN cat_state as b on (b.id=a.state_id) WHERE a.id=?;",id)

    return render_template('tarea.html',nota=nota)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)