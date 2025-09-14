from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = "asdlkjashdasd87as9dhasd9dsakhdkjsahdkasdas7dasd"

# Intitalize Database
def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   username TEXT UNIQUE NOT NULL,
                   password TEXT NOT NULL,
                   email TEXT UNIQUE NOT NULL, 
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                   )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   description TEXT,
                   user_id INTEGER NOT NULL, 
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   FOREIGN KEY (user_id) REFERENCES users (id)
                   )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL,
                   description TEXT,
                   completed BOOLEAN DEFAULT FALSE, 
                   project_id INTEGER NOT NULL, 
                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   completed_at TIMESTAMP,
                   FOREIGN KEY (project_id) REFERENCES projects (id)
                   )
    ''')

    conn.commit()
    conn.close()

# Helper functions
def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response 

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close() 
        if user and user['password'] == get_hash_password(password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login succesful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username and/or password invalid', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template(url_for('register'))
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email)).fetchone()
        if user:
            flash('Username or email already exists.', 'error')
            return render_template(url_for('register'))
        hashed_password = get_hash_password(password)
        conn.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
        conn.commit()
        conn.close()
        flash('Account created!', 'success')
        return  redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
        

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()

    projects = conn.execute("SELECT * FROM projects WHERE user_id=? ORDER BY created_at DESC", (session['user_id'],))

    return render_template('dashboard.html', projects=projects)


@app.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        if not name:
            flash('Project name is mandatory.', 'error')
            return render_template('new_project.html')
        
        conn = get_db_connection()
        conn.execute("INSERT INTO projects (name, description, user_id) VALUES(?, ?, ?)",
                     (name, description, session['user_id']))
        
        conn.commit()
        conn.close()

        flash('Project created!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('new_project.html')


@app.route('/project/<int:project_id>')
@login_required
def view_project(project_id):
    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE id=? AND user_id=?", (project_id, session['user_id'])).fetchone()

    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('dashboard'))
    
    tasks = conn.execute("SELECT * FROM tasks WHERE project_id=? ORDER BY completed ASC, created_at DESC", (project_id,)).fetchall()
    
    conn.close()
    return render_template('project.html', project=project, tasks=tasks)


@app.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE id=? AND user_id=?", (project_id, session['user_id'])).fetchone()

    if not project:
        flash('Project not found.', 'error')
        return redirect('dashboard')
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']

        if not name:
            flash('Name is mandatory.', 'error')
            return render_template('edit_project.html', project=project)
        
        conn.execute("UPDATE projects SET name=?, description=? WHERE id=?", (name, description, project_id))
        conn.commit()
        conn.close()

        flash('Project updated.', 'success')
        return redirect(url_for('view_project', project_id=project_id))
    
    return render_template('edit_project.html', project=project)


@app.route('/project/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    conn = get_db_connection()
    project = conn.execute("SELECT * FROM projects WHERE id=? AND user_id=?", (project_id, session['user_id'])).fetchone()

    if not project:
        flash('Project not found.', 'error')
        return redirect('dashboard')
    
    conn.execute("DELETE FROM tasks WHERE project_id=?", (project_id,))
    conn.execute("DELETE FROM projects WHERE id=?", (project_id,))
    conn.commit()
    conn.close()

    flash('Project and associated tasks deleted.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/project/<int:project_id>/task/new', methods=['GET', 'POST'])
@login_required
def new_task(project_id):
    conn = get_db_connection()

    project = conn.execute("SELECT * FROM projects WHERE id=? AND user_id=?", (project_id, session['user_id'])).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        if not title:
            flash('Title is mandatory', 'error')
            return render_template('new_task.html', project=project)
        
        conn.execute("INSERT INTO tasks (title, description, project_id) VALUES (?, ?, ?)",
                     (title, description, project_id))
        
        conn.commit()
        conn.close()

        flash('Task created!', 'success')
        return redirect(url_for('view_project', project_id=project_id))
         
    return render_template('new_task.html', project=project)


@app.route('/task/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    conn = get_db_connection()

    task = conn.execute("""SELECT t.*, p.user_id FROM tasks t 
                        JOIN projects p ON p.id=t.project_id
                        WHERE t.id=? AND p.user_id=?""",
                        (task_id, session['user_id'])).fetchone()
    
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('dashboard'))
    
    new_status = not task['completed']
    completed_at = datetime.now() if new_status else None

    conn.execute("UPDATE tasks SET completed=?, completed_at=? WHERE id=?", (new_status, completed_at, task_id))
    conn.commit()
    conn.close()

    status = 'completed' if new_status else 'marked incomplete'
    message = "Task " + status 
    flash(message, 'success')
    return redirect(url_for('view_project', project_id=task['project_id']))


@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    conn = get_db_connection()

    conn = get_db_connection()

    task = conn.execute("""SELECT t.*, p.user_id, p.name as project_name FROM tasks t 
                        JOIN projects p ON p.id=t.project_id
                        WHERE t.id=? AND p.user_id=?""",
                        (task_id, session['user_id'])).fetchone()
    
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        if not title:
            flash('Title is mandatory.', 'error')
            return render_template('edit_task.html', task=task)
        
        conn.execute("UPDATE tasks SET title=?, description=? WHERE id=?", (title, description, task_id))
        conn.commit()
        conn.close()

        flash('Task updated.', 'success')
        return redirect(url_for('view_project', project_id=task['project_id']))
    
    return render_template('edit_task.html', task=task)


@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    conn = get_db_connection()

    task = conn.execute("""SELECT t.*, p.user_id FROM tasks t 
                        JOIN projects p ON p.id=t.project_id
                        WHERE t.id=? AND p.user_id=?""",
                        (task_id, session['user_id'])).fetchone()
    
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('dashboard'))
    
    project_id = task['project_id']
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

    flash('Task deleted.', 'success')
    return redirect(url_for('view_project', project_id=project_id))


@app.route('/completed')
@login_required
def completed_tasks():
    conn = get_db_connection()
    tasks = conn.execute("""
                        SELECT t.*, p.name as project_name 
                        FROM tasks t 
                        JOIN projects p ON p.id=t.project_id 
                        WHERE t.completed=TRUE AND p.user_id=? 
                        ORDER BY t.completed_at DESC
                    """, (session['user_id'],)).fetchall()

    conn.close()
    return render_template('completed.html', tasks=tasks)    


if __name__ == '__main__':
    init_db()
    app.run(debug=True)