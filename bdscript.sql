CREATE TABLE cat_state(
 id INTEGER PRIMARY KEY
,name TEXT NOT NULL
,description TEXT 
,created_at DATETIME
);

CREATE TABLE tbl_user(
 id INTEGER PRIMARY KEY
,user_name TEXT UNIQUE NOT NULL
,user_email TEXT UNIQUE NOT NULL
,user_password TEXT NOT NULL
,user_photo TEXT 
,state_id INTEGER 
,created_at DATETIME NOT NULL
,FOREIGN KEY (state_id) REFERENCES cat_state(id)
);

CREATE TABLE tbl_session(
 id INTEGER PRIMARY KEY
,user_id INTEGER NOT NULL
,session_start DATETIME NOT NULL
,session_end DATETIME
,created_at DATETIME NOT NULL,
FOREIGN KEY (user_id) REFERENCES tbl_user(id)
);

CREATE TABLE tbl_work_space(
 id INTEGER PRIMARY KEY
,title TEXT NOT NULL
,topic TEXT NOT NULL
,isPersonal INT NOT NULL
,owner INT NOT NULL
,description TEXT NOT NULL
,state_id INTEGER NOT NULL
,created_at DATETIME NOT NULL
,FOREIGN KEY (state_id) REFERENCES cat_state(id)
,FOREIGN KEY (owner) REFERENCES tbl_user(id)
);

##Solicitudes de union a grupos de trabajo
CREATE TABLE tbl_work_space_member_invitation(
 id INTEGER PRIMARY KEY
,work_space_id INTEGER NOT NULL
,user_id INTEGER NOT NULL
,state_id INTEGER NOT NULL
,created_by INTEGER NOT NULL
,created_at DATETIME NOT NULL
,FOREIGN KEY (work_space_id) REFERENCES tbl_work_space(id)
,FOREIGN KEY (user_id) REFERENCES tbl_user(id)
,FOREIGN KEY (created_by) REFERENCES tbl_user(id)
,FOREIGN KEY (state_id) REFERENCES cat_state(id)
);

##Miembros del espacio de trabajo
CREATE TABLE tbl_work_space_member(
 id INTEGER PRIMARY KEY 
,work_space_id INTEGER NOT NULL
,user_id INTEGER NOT NULL
,created_at DATETIME NOT NULL
,FOREIGN KEY (work_space_id) REFERENCES tbl_work_space(id)
,FOREIGN KEY (user_id) REFERENCES tbl_user(id)
);

CREATE TABLE tbl_note(
 id INTEGER PRIMARY KEY
,work_space_id INTEGER NOT NULL
,title TEXT NOT NULL
,description TEXT NOT NULL
,state_id INTEGER NOT NULL
,created_at DATETIME NOT NULL
,FOREIGN KEY(work_space_id) REFERENCES tbl_work_space(id)
,FOREIGN KEY (state_id) REFERENCES cat_state(id)
);

CREATE TABLE tbl_reminder(
 id INTEGER PRIMARY KEY 
,work_space_id INTEGER NOT NULL
,title TEXT NOT NULL
,description TEXT NOT NULL
,reminder_date DATETIME NOT NULL 
,state_id INTEGER NOT NULL
,created_at DATETIME NOT NULL
,FOREIGN KEY(work_space_id) REFERENCES tbl_work_space(id)
,FOREIGN KEY (state_id) REFERENCES cat_state(id)
);

CREATE TABLE tbl_task(
 id INTEGER PRIMARY KEY 
,work_space_id INTEGER NOT NULL
,title TEXT NOT NULL
,description TEXT NOT NULL
,expired_date DATETIME 
,state_id INTEGER NOT NULL
,created_by INTEGER NOT NULL
,created_at DATETIME NOT NULL
,FOREIGN KEY(work_space_id) REFERENCES tbl_work_space(id)
,FOREIGN KEY (state_id) REFERENCES cat_state(id)
,FOREIGN KEY (created_by) REFERENCES tbl_user(id)
);

##Miembros que pertenecen a una tarea
CREATE TABLE tbl_task_member(
 id INTEGER PRIMARY KEY
,task_id INTEGER NOT NULL
,user_id INTEGER NOT NULL
,FOREIGN KEY (task_id) REFERENCES tbl_task(id)
,FOREIGN KEY (user_id) REFERENCES tbl_user(id)
);

##Actividades que componen a una tarea
CREATE TABLE tbl_task_activity(
 id INTEGER PRIMARY KEY
,task_id INTEGER NOT NULL
,activity TEXT NOT NULL
,state_id INTEGER NOT NULL
,user_asigned INTEGER
,expired_date DATETIME
,created_at DATETIME NOT NULL
,FOREIGN KEY (user_asigned) REFERENCES tbl_user(id)
,FOREIGN KEY (task_id) REFERENCES tbl_task(id)
,FOREIGN KEY (state_id) REFERENCES cat_state(id)
);

CREATE TABLE cat_permission(
 id INTEGER PRIMARY KEY
,name TEXT NOT NULL
,description TEXT
,created_at DATETIME NOT NULL
);

CREATE TABLE tbl_work_space_permission(
 id INTEGER PRIMARY KEY NOT NULL
,work_space_id INTEGER NOT NULL
,user_id INTEGER NOT NULL
,permission_id INTEGER NOT NULL
,FOREIGN KEY (permission_id) REFERENCES cat_permission (id)
);

/* Inserciones */
INSERT INTO cat_state (name, description) VALUES 
 ('Active','Active State')
,('Inactive','Inactive State');