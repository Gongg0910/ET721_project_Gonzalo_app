import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "dev_secret_key"

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------ #
# DATABASE CONNECTION #
# ------------------ #
def get_db():
    conn = sqlite3.connect("flask_auth.db")
    conn.row_factory = sqlite3.Row
    return conn

""" It is a must required in order to work for image.html upload/delete, otherwise it won't work and shut down whole webpages"""
def login_required(w):
    from functools import wraps
    @wraps(w)
    def function(*a, **b):
        if 'username' not in session:
            return redirect(url_for('login'))
        return w(*a, **b)
    return function

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
@login_required
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


# ------------------------------------------------------------------------------------------------------------------------------------------------#
# TO DO BLOG and COMMENT
# ------------------------------------------------------------------------------------------------------------------------------------------------#
# ------------------ #
# BLOG and COMMENT   #
# ------------------ #
@app.route('/blog')
@login_required
def blog_1():

    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT blog.id, users.username, blog.title, blog.content, blog.created_at, blog.is_edited 
        FROM blog 
        JOIN users ON blog.user_id = users.id
        ORDER BY blog.created_at DESC
    """)
    blog_rows = cursor.fetchall()
    
    blogs_data = []
    for row in blog_rows:
        blog_dict = dict(row)  
        
        cursor.execute("""
            SELECT username, comment_text, created_at 
            FROM comments 
            WHERE blog_id = ? 
            ORDER BY created_at ASC
        """, (blog_dict['id'],))
        
        blog_dict['comments'] = cursor.fetchall()
        blogs_data.append(blog_dict)
        
    conn.close()
    
    return render_template('blogs.html', username=session['username'], blogs=blogs_data)


@app.route('/add_blog', methods=['POST'])
@login_required
def add_blog(): 
    title = request.form['title']
    content = request.form['content']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (session['username'],))
    user = cursor.fetchone()
    
    if user:
        cursor.execute("INSERT INTO blog (user_id, title, content) VALUES (?, ?, ?)", (user['id'], title, content))
        conn.commit()
        
    conn.close()
    return redirect(url_for('blog_1'))


@app.route('/index_blog')
@login_required
def index_blog():
    if 'username' in session:
        return render_template('index_blog.html')
    return redirect(url_for('login'))


@app.route('/edit_blog/<int:blog_id>', methods=['POST'])
@login_required
def edit_blog(blog_id):

    data = request.get_json()
    new = data.get('content')
     
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT blog.id FROM blog 
        JOIN users ON blog.user_id = users.id 
        WHERE blog.id = ? AND users.username = ?
    """, (blog_id, session['username']))
    post = cursor.fetchone()
    
    if post:
        cursor.execute("""
            UPDATE blog 
            SET content = ?, is_edited = 1 
            WHERE id = ?
        """, (new.strip(), blog_id))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
        
    conn.close()


@app.route('/add_comment/<int:blog_id>', methods=['POST'])
@login_required
def add_comment(blog_id):
    
    comment_text = request.form.get('comment_text')
    if comment_text and comment_text.strip() != "":
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO comments (blog_id, username, comment_text) VALUES (?, ?, ?)",
            (blog_id, session['username'], comment_text.strip())
        )
        conn.commit()
        conn.close()
        
    return redirect(url_for('blog_1'))


@app.route('/like_blog/<int:blog_id>', methods=['POST'])
@login_required
def like_blog(blog_id):
  
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT likes FROM blog WHERE id = ?", (blog_id,))
    blog = cursor.fetchone()
    
    if blog:
        new_likes = blog['likes'] + 1
        cursor.execute("UPDATE blog SET likes = ? WHERE id = ?", (new_likes, blog_id))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'likes': new_likes})
        
    conn.close()
# ------------------------------------------------------------------------------------------------------------------------------------------------#
# TTO DO BLOG and COMMENT
# ------------------------------------------------------------------------------------------------------------------------------------------------#

# ------------------------------------------------------------------------#
# All 3 routes #
# ------------------------------------------------------------------------#
@app.route('/todo')
@login_required
def todo_list():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

# @app.route('/blog')
# def blog_1():
#     if 'username' in session:
#         return render_template('blog.html', username=session['username'])
#     return redirect(url_for('login'))

# @app.route('/image')
# def image_1():
#     if 'username' in session:
#         return render_template('image.html', username=session['username'])
#     return redirect(url_for('login'))
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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

# ------------------ #
# Load image.html    #
# ------------------ #
@app.route('/image')
@login_required
def image_1():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM images ORDER BY uploaded_at DESC")

    images = cursor.fetchall()
    conn.close()
    return render_template('image.html', username=session['username'], images=images)

# ------------------ #
# UPLOAD IMAGE       #
# ------------------ #
@app.route('/upload', methods=["POST"])
@login_required
def upload_image():

    file = request.files['image']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        """ locate static/uploads in order to upload images"""
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO images (filename) VALUES (?)", (filename,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Image uploaded successfully!'})
    
# ------------------ #
# DELETE IMAGE       #
# ------------------ #
@app.route('/delete_image_file/<int:image_id>', methods=['DELETE'])
@login_required
def delete_image_file(image_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT filename FROM images WHERE id = ?", (image_id,))

    cursor.execute("DELETE FROM images WHERE id = ?", (image_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Image deleted successfully'})

# ------------------
# RUN APP
# ------------------
if __name__ =='__main__':
    app.run(debug=True)