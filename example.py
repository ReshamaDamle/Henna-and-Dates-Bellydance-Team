"""
Concept: Flask + HTML Integration

This example demonstrates Flask web framework with HTML templates.
Students will learn about web routes, template rendering, and dynamic content.
"""

# Task 10 - Flask + HTML Integration (Example File)
# This file demonstrates Flask with HTML templates

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Simple file-based storage
USERS_FILE = 'users.json'
CONTACTS_FILE = 'contacts.json'
CHECKLISTS_FILE = 'checklists.json'

def load_data():
    users = {}
    contacts = {}
    checklists = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, 'r') as f:
            contacts = json.load(f)
    if os.path.exists(CHECKLISTS_FILE):
        with open(CHECKLISTS_FILE, 'r') as f:
            checklists = json.load(f)
    return users, contacts, checklists

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def save_contacts(contacts):
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f)

def save_checklists(checklists):
    with open(CHECKLISTS_FILE, 'w') as f:
        json.dump(checklists, f)


def is_prime(n):
    """Check if a number is prime"""
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def next_prime(n):
    """Find the next prime number after n"""
    p = n + 1
    while not is_prime(p):
        p += 1
    return p


@app.route("/")
def home():
    if 'username' in session:
        return render_template(
            "index.html", 
            title="Henna and Dates Dancers", 
            message=f"Welcome back, {session['username']}! 💃✨",
            logged_in=True,
            username=session['username']
        )
    else:
        return render_template(
            "index.html", 
            title="Henna and Dates Dancers", 
            message="Sign in to manage the Henna and Dates dancers! 💃✨",
            logged_in=False
        )
    
@app.route("/about")
def about():
    return render_template(
        "index.html", title="About Page", message="This is the about page!"
    )

# Authentication routes
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({"success": False, "message": "Yalla! Your username and password are required"})
    
    users, contacts, checklists = load_data()
    if username in users:
        return jsonify({"success": False, "message": "Username already exists"})
    
    users[username] = password
    contacts[username] = {}
    
    # Initialize with default checklist tasks
    default_tasks = [
        {"task": "Pack fake eyelashes", "completed": False},
        {"task": "Spray anti-bacterial spray on costumes", "completed": False},
        {"task": "Bring extra performance shoes", "completed": False},
        {"task": "Pack make-up bag", "completed": False},
        {"task": "Check costume zippers and hooks", "completed": False},
        {"task": "Pack backup jewelry", "completed": False},
        {"task": "Bring water bottle", "completed": False},
        {"task": "Pack hair accessories", "completed": False},
        {"task": "Check music files", "completed": False},
        {"task": "Pack emergency sewing kit", "completed": False}
    ]
    checklists[username] = default_tasks
    
    save_users(users)
    save_contacts(contacts)
    save_checklists(checklists)
    
    session['username'] = username
    return jsonify({"success": True, "message": "Account created!"})

@app.route("/signin", methods=["POST"])
def signin():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    users, _, _ = load_data()
    if username in users and users[username] == password:
        session['username'] = username
        return jsonify({"success": True, "message": "Signed in!"})
    
    return jsonify({"success": False, "message": "Invalid credentials"})

@app.route("/signout")
def signout():
    session.pop('username', None)
    return redirect(url_for('home'))

# Contact management routes
@app.route("/contacts")
def get_contacts():
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    _, contacts, _ = load_data()
    return jsonify(contacts.get(session['username'], {}))

@app.route("/add_contact", methods=["POST"])
def add_contact():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    
    if not name or not phone:
        return jsonify({"success": False, "message": "Name and phone required"})
    
    _, contacts, _ = load_data()
    if session['username'] not in contacts:
        contacts[session['username']] = {}
    
    contacts[session['username']][name] = phone
    save_contacts(contacts)
    return jsonify({"success": True, "message": "Contact added!"})

@app.route("/search_contact")
def search_contact():
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    name = request.args.get("name", "").strip()
    if not name:
        return "Name required", 400
    
    _, contacts, _ = load_data()
    user_contacts = contacts.get(session['username'], {})
    return user_contacts.get(name, "Not found")

# Checklist management routes
@app.route("/checklist")
def get_checklist():
    if 'username' not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    _, _, checklists = load_data()
    return jsonify(checklists.get(session['username'], []))

@app.route("/toggle_task", methods=["POST"])
def toggle_task():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    data = request.get_json()
    task_index = data.get('index')
    
    if task_index is None:
        return jsonify({"success": False, "message": "Task index required"})
    
    _, _, checklists = load_data()
    user_checklist = checklists.get(session['username'], [])
    
    if 0 <= task_index < len(user_checklist):
        user_checklist[task_index]['completed'] = not user_checklist[task_index]['completed']
        save_checklists(checklists)
        return jsonify({"success": True, "message": "Task updated!"})
    
    return jsonify({"success": False, "message": "Invalid task index"})

@app.route("/add_task", methods=["POST"])
def add_task():
    if 'username' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401
    
    data = request.get_json()
    task_text = data.get('task', '').strip()
    
    if not task_text:
        return jsonify({"success": False, "message": "Task text required"})
    
    _, _, checklists = load_data()
    if session['username'] not in checklists:
        checklists[session['username']] = []
    
    checklists[session['username']].append({"task": task_text, "completed": False})
    save_checklists(checklists)
    return jsonify({"success": True, "message": "Task added!"})


if __name__ == "__main__":
    app.run(debug=True)