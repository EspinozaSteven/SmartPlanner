# SmartPlanner

## Video demo:
https://youtu.be/jaQ1ECCKFzU

# Descripción general:
Este proyecto trata de un sistema que permita a los usuarios crear tareas sobre las actividades (ya sean personales o grupales) que se desea realizar en un tiempo determinado, con el fin de realizar una mejor administración de tiempo del usuario.

Para el desarrollo de este proyecto se utilizo python, tailwind, css, bootstrap, sqlite y GitHub para el control de versiones

## Estructura del sistema
### Login y registro
Esto permite que un usuario tenga la capacidad de crear un usuario con el fin de ingresar al sistema, siendo esto una parte común, pero de vital importancia dentro de cualquier sistema, formando parte de la seguridad cibernetica de cada usuario.

### Configuración del sistema
Permite que los usuarios puedan modificar su información inicial del sistema, permitiendo cambios como el nombre de usuario o contraseña; además de tener la opción de incluir una foto de perfil.

### Espacios de trabajo (WorkSpace)
Permite al usuario crear dos tipos de WorkSpace, personal y grupales.
Los WorkSpace personales tienen el proposito de gestionar todas las tareas del usuario donde no se encuentren involucradas otras personas, por otra parte los WorkSpace grupales permite integran a diversos usuarios para las activiades colectivas, creando una mejor organización y orden cuando desarrollen sus tareas.

### Creación de tareas, notas y recordatorios
Permite al usuario la creación de tareas, notas o recordatorios; para este punto, se le presentara un formulario al usuario donde solicite información como "Titulo", "Descripción", "Actividades" y "Fecha de expiración".

### Visualización de tareas, notas y recordatorios
Esta es una interfaz que muestra al usuario cuales son todas las tareas, notas o recordatorios que haya ingresado, esto tiene la finalidad que el usuario, tenga la capacidad de ordenar e identificar cuales son las actividades pendientes y saber darles prioridad.

### Invitación para un WorkSpace
Esto solo puede realizarse para los WorkSpace grupales, siendo un medio para invitar a diversos usuarios al espacio de trabajo; enviando un correo electronico a todos los usuarios para integrarse formalmente al grupo

### Gestión de tareas y asignación de actividades
Cuando se crea un WorkSpace grupal, para garantizar un orden entre los miembros del equipo, el creador del WorkSpace tiene la capacidad de asignar tareas a cada uno de los integrantes del equipo; además, tendra la capacidad de dar seguimiento a todas las tareas realizadas, permitiendo una mejor gestión de estas.

### Roles y privilegios
#### Gestor
- El gestor tendra la capacidad de crear, buscar, actualizar, y eliminar notas, recordatorios y tareas. Las tareas, tendran la excepción de no ser eliminadas si algun integrante ha trabajado en ella.
- Asignar privilegios a los integrantes del WorkSpace

#### Encargado de tareas
- Podra crear nuevas actividades y asignarlas a los participantes

#### Integrantes
- Podra crear, buscar, actualizar y eliminar notas, recordatorios y tareas. Las tareas, tendran la excepción de no ser eliminadas si algun integrante ha trabajado en ella.

## Interfaces
### Home
- Poseera un navbar que muestra la información del usuario
- Tendra un sidebar que mostrara un menu con la siguiente información: notas, recordatorios, tareas, espacios de trabajo y configuración
- El dashboard muestra inicialmente el espacio de trabajo personal

### Interfaz de notas
- Esta interfaz mostrara los registros de notas de forma descendete segun la fecha de creación junto con el espacio de trabajo en el que pertenece
- Incluye un boton para eliminar la nota

### Interfaz de recordatorios
- Mostrara los registros de recordatorios de forma ascendente según fecha recordatoria y deberá indicar de qué espacio de trabajo pertenece. 
- Permitir mostrar los recordatorios caducados y tener la opción de eliminarlos

### Interfaz de tareas
- Mostrara los registros de tareas de forma descendente según fecha creación y deberá indicar de qué espacio de trabajo pertenece. 
- Incluye un botón que permite visualizar la información completa sobre la tarea

### Interfaz de espacios de trabajo
- La interfaz muestra el sidebar junto con el menu de la interfaz
- Presenta un cuadro con el nombre "Crea un espacio de trabajo", donde, una vez hecho click se abrira una formulario que solicitara la información requerida para crear un espacio de trabajo
- Se mostrara todos los espacio de trabajo que el usuario haya creado.

### Configuración
- Muestra el sidebar con el menu
- Muestra un cuadro que permite pre visualizar al usuario su foto de perfil
- Muestra un formulario donde solocita al usuario la información básica que desea modificar
