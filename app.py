import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

app = Flask(__name__)
app.secret_key = "dev_secret_key"

# ------------------ #
# DATABASE CONNECTION #
# ------------------ #
def get_db():
    conn = sqlite3.connect("flask_auth.db")
    conn.row_factory = sqlite3.Row
    return conn

# ------------------ #
# LOADING PAGE       #
# ------------------ #
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# ------------------ #
# LOGIN ROUTING      #
# ------------------ #
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        
        if user:
            session['username'] = user['username']
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password")
            conn.close()
            
    return render_template("login.html")

# ------------------ #
# DASHBOARD ROUTING  #
# ------------------ #
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

# ------------------ #
# LOGOUT ROUTING     #
# ------------------ #
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ------------------ #
# SIGNUP ROUTING     #
# ------------------ #
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?,?,?)", (username, email, password))
            conn.commit()
            flash("Account created successfully!")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email and username already exists!')
        finally:
            conn.close()
    return render_template('signup.html')



# ------------------------------------------------------------------------#
# All 3 routes #
# ------------------------------------------------------------------------#
@app.route('/todo')
def todo_list():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/blog')
def blog_1():
    if 'username' in session:
        return render_template('blog.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/image')
def image_1():
    if 'username' in session:
        return render_template('image.html', username=session['username'])
    return redirect(url_for('login'))
# ------------------------------------------------------------------------#
# All routes #
# ------------------------------------------------------------------------#



# ------------------------------------------------------------------------------------------------------------------------------------------------#
# TO DO LIST TASKS
# ------------------------------------------------------------------------------------------------------------------------------------------------#
# ------------------ #
# GET ALL TASKS      #
# ------------------ #
@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    user = cursor.fetchone()

    cursor.execute("SELECT id, task, completed FROM tasks WHERE user_id = ?", (user['id'],))
    tasks = cursor.fetchall()
    conn.close()
    return jsonify([{"id": row["id"], "task": row["task"], "completed": row["completed"]} for row in tasks])

# ------------------ #
# ADD NEW TASK       #
# ------------------ #
@app.route('/add_task', methods=['POST'])
def add_task():

    data = request.get_json()
    task_text = data.get('task')
    
    if task_text:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
        user = cursor.fetchone()

        if user:
            cursor.execute("INSERT INTO tasks (user_id, task) VALUES (?, ?)", (user['id'], task_text))
            conn.commit()
            conn.close()
            return jsonify({'status': 'success'})
            
        conn.close()
        
    return jsonify({'status': 'error'})

# ------------------ #
# DELETE A TASK      #
# ------------------ #
@app.route('/delete_task', methods=['POST'])
def delete_task():

    data = request.get_json()
    task_id = data.get('id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    user = cursor.fetchone()
    
    if user:
        cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user['id']))
        conn.commit()
        
    conn.close()
    return jsonify({'status': 'deleted'})

# ------------------ #
# COMPLETE A TASK    #
# ------------------ #
@app.route('/toggle_task', methods=['POST'])
def toggle_task():
    data = request.get_json()
    task_id = data.get('id')
    completed_status = data.get('completed') 
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    user = cursor.fetchone()
    if user:
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?", (completed_status, task_id, user['id']))
        conn.commit()
    conn.close()
    return jsonify({'status': 'updated'})

# ------------------ #
# UPDATE A TASK      #
# ------------------ #
@app.route('/update_task', methods=['POST'])
def update_task():

    data = request.get_json()
    task_id = data.get('id')
    new_text = data.get('task')
      
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    user = cursor.fetchone()
    
    if user:
        cursor.execute("UPDATE tasks SET task = ? WHERE id = ? AND user_id = ?", (new_text.strip(), task_id, user['id']))
        conn.commit()
        
    conn.close()
    return jsonify({'status': 'updated'})
# ------------------------------------------------------------------------------------------------------------------------------------------------#
# TO DO LIST TASKS
# ------------------------------------------------------------------------------------------------------------------------------------------------#

























# ------------------
# RUN APP
# ------------------
if __name__ =='__main__':
    app.run(debug=True)