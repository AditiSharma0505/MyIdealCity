# # import mysql.connector
# # from mysql.connector import Error
# # from flask import Flask, render_template, request, redirect, url_for, session, flash
# # from werkzeug.security import generate_password_hash, check_password_hash
# # from werkzeug.utils import secure_filename
# # import os
# # from datetime import datetime

# # app = Flask(__name__)
# # app.secret_key = "supersecretkey"
# # app.config['UPLOAD_FOLDER'] = 'static/uploads'
# # app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

# # # Ensure upload directory exists
# # os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# # # ---------- MySQL connection helper ----------
# # db = None

# # def get_db():
# #     """Get a live MySQL connection; reconnect if needed."""
# #     global db
# #     try:
# #         if db is None or not db.is_connected():
# #             db = mysql.connector.connect(
# #                 host="localhost",
# #                 user="root",
# #                 password="1234",  # ← Make sure this is your correct MySQL password!
# #                 database="myidealcity"
# #             )
# #         return db
# #     except Error as err:
# #         # DON'T crash the app - just print the error and return None
# #         print(f"⚠️ Database connection failed: {err}")
# #         return None

# # # Try an initial connect (optional)
# # try:
# #     connection = get_db()
# #     if connection:
# #         print("✅ Database connected successfully!")
# #         connection.close()  # Close the test connection
# #     else:
# #         print("⚠️ Database connection failed, but app will continue")
# # except Exception as e:
# #     print(f"⚠️ Database connection issue: {e}")

# # # ---------------- ROUTES ----------------

# # @app.route("/")
# # def index():
# #     return render_template("index.html")

# # @app.route("/complaint")
# # def complaint_form():
# #     if "user_id" not in session:
# #         return redirect(url_for("userlogin"))
# #     return render_template("complaint.html", user=session["user_name"])

# # @app.route("/submit-complaint", methods=["POST"])
# # def submit_complaint():
# #     if "user_id" not in session:
# #         return redirect(url_for("userlogin"))
    
# #     try:
# #         name = request.form.get("name")
# #         email = request.form.get("email")
# #         category = request.form.get("category")
# #         complaint_text = request.form.get("complaint")
# #         locality = request.form.get("locality")
        
# #         # Handle file upload
# #         evidence_filename = None
# #         if 'evidence' in request.files:
# #             file = request.files['evidence']
# #             if file and file.filename != '':
# #                 filename = secure_filename(file.filename)
# #                 # Add timestamp to make filename unique
# #                 evidence_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
# #                 file.save(os.path.join(app.config['UPLOAD_FOLDER'], evidence_filename))

# #         conn = get_db()
# #         cur = conn.cursor()
# #         cur.execute(
# #             "INSERT INTO complaints (user_id, name, email, category, complaint, locality, evidence_filename, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
# #             (session["user_id"], name, email, category, complaint_text, locality, evidence_filename, "Pending")
# #         )
# #         conn.commit()
# #         cur.close()
        
# #         flash("Complaint submitted successfully!", "success")
# #         return redirect(url_for("dashboard"))
    
# #     except Exception as e:
# #         flash(f"Error submitting complaint: {str(e)}", "error")
# #         return redirect(url_for("complaint_form"))

# # @app.route("/dashboard")
# # def dashboard():
# #     if "user_id" not in session:
# #         return redirect(url_for("userlogin"))
    
# #     user_locality = session.get("locality", None)
# #     user_id = session.get("user_id")

# #     conn = get_db()
# #     cur = conn.cursor(dictionary=True)

# #     # Get user's complaints
# #     cur.execute(
# #         "SELECT id, category, complaint, status, upvotes, locality, created_at FROM complaints WHERE user_id = %s ORDER BY id DESC",
# #         (user_id,)
# #     )
# #     user_complaints = cur.fetchall()

# #     # Get locality complaints for upvoting
# #     if user_locality:
# #         cur.execute(
# #             "SELECT id, category, complaint, status, upvotes, locality FROM complaints WHERE locality=%s ORDER BY id DESC",
# #             (user_locality,)
# #         )
# #     else:
# #         cur.execute("SELECT id, category, complaint, status, upvotes, locality FROM complaints ORDER BY id DESC")

# #     locality_complaints = cur.fetchall()
# #     cur.close()

# #     return render_template("dashboard.html", 
# #                          user_complaints=user_complaints, 
# #                          locality_complaints=locality_complaints, 
# #                          locality=user_locality)

# # @app.route("/upvote/<int:complaint_id>")
# # def upvote(complaint_id):
# #     if "user_id" not in session:
# #         return redirect(url_for("userlogin"))
    
# #     conn = get_db()
# #     cur = conn.cursor()
# #     cur.execute("UPDATE complaints SET upvotes = upvotes + 1 WHERE id = %s", (complaint_id,))
# #     conn.commit()
# #     cur.close()
    
# #     return redirect(url_for("dashboard"))

# # @app.route("/delete-complaint/<int:complaint_id>")
# # def delete_complaint(complaint_id):
# #     if "user_id" not in session:
# #         return redirect(url_for("userlogin"))
    
# #     conn = get_db()
# #     cur = conn.cursor()
    
# #     # Verify the complaint belongs to the user
# #     cur.execute("SELECT user_id FROM complaints WHERE id = %s", (complaint_id,))
# #     result = cur.fetchone()
    
# #     if result and result[0] == session["user_id"]:
# #         # Get evidence filename to delete the file
# #         cur.execute("SELECT evidence_filename FROM complaints WHERE id = %s", (complaint_id,))
# #         evidence_file = cur.fetchone()
        
# #         # Delete the complaint
# #         cur.execute("DELETE FROM complaints WHERE id = %s", (complaint_id,))
# #         conn.commit()
        
# #         # Delete evidence file if exists
# #         if evidence_file and evidence_file[0]:
# #             try:
# #                 os.remove(os.path.join(app.config['UPLOAD_FOLDER'], evidence_file[0]))
# #             except:
# #                 pass  # Silently fail if file doesn't exist
    
# #     cur.close()
# #     return redirect(url_for("dashboard"))

# # # ------------- Authentication Routes -------------

# # @app.route("/register", methods=["GET", "POST"])
# # def register():
# #     if request.method == "POST":
# #         gov_id_type = request.form.get("gov_id_type")
# #         gov_id_number = request.form.get("gov_id_number")
# #         name = request.form.get("name")
# #         email = request.form.get("email")
# #         password = request.form.get("password")
# #         locality = request.form.get("locality")

# #         hashed_pw = generate_password_hash(password)

# #         try:
# #             conn = get_db()
# #             cur = conn.cursor()
# #             cur.execute("""
# #                 INSERT INTO users (gov_id_type, gov_id_number, name, email, password, locality)
# #                 VALUES (%s, %s, %s, %s, %s, %s)
# #             """, (gov_id_type, gov_id_number, name, email, hashed_pw, locality))
# #             conn.commit()
# #             cur.close()
            
# #             flash("Registration successful! Please login.", "success")
# #             return redirect(url_for("userlogin"))
        
# #         except mysql.connector.IntegrityError:
# #             flash("Government ID or Email already exists!", "error")
# #             return render_template("register.html")
    
# #     return render_template("register.html")

# # @app.route("/userlogin", methods=["GET", "POST"])
# # def userlogin():
# #     if request.method == "POST":
# #         gov_id_number = request.form.get("gov_id_number")
# #         password = request.form.get("password")

# #         conn = get_db()
# #         cur = conn.cursor(dictionary=True)
# #         cur.execute("SELECT * FROM users WHERE gov_id_number=%s", (gov_id_number,))
# #         user = cur.fetchone()
# #         cur.close()

# #         if user and check_password_hash(user["password"], password):
# #             session["user_id"] = user["id"]
# #             session["user_name"] = user["name"]
# #             session["locality"] = user["locality"]
# #             return redirect(url_for("dashboard"))
# #         else:
# #             return render_template("userlogin.html", error="Invalid ID or Password")

# #     return render_template("userlogin.html")

# # @app.route("/logout-user")
# # def logout_user():
# #     session.pop("user_id", None)
# #     session.pop("user_name", None)
# #     session.pop("locality", None)
# #     return redirect(url_for("index"))

# # # ------------- Admin Routes -------------

# # @app.route("/admin-login", methods=["GET", "POST"])
# # def admin_login():
# #     if request.method == "POST":
# #         official_id = request.form.get("official_id")
# #         password = request.form.get("password")

# #         conn = get_db()
# #         cur = conn.cursor(dictionary=True)
# #         cur.execute("SELECT * FROM officials WHERE official_id=%s AND is_active=TRUE", (official_id,))
# #         official = cur.fetchone()
# #         cur.close()

# #         if official and check_password_hash(official["password_hash"], password):
# #             session["admin_logged_in"] = True
# #             session["official_id"] = official["official_id"]
# #             session["official_name"] = official["name"]
# #             return redirect(url_for("admin_dashboard"))
        
# #         return render_template("adminlogin.html", error="Invalid Official ID or Password")
    
# #     return render_template("adminlogin.html")

# # @app.route("/admin")
# # def admin_dashboard():
# #     if not session.get("admin_logged_in"):
# #         return redirect(url_for("admin_login"))

# #     conn = get_db()
# #     cur = conn.cursor(dictionary=True)
    
# #     # Get stats
# #     cur.execute("SELECT COUNT(*) as total FROM complaints")
# #     total = cur.fetchone()['total']
    
# #     cur.execute("SELECT COUNT(*) as pending FROM complaints WHERE status='Pending'")
# #     pending = cur.fetchone()['pending']
    
# #     cur.execute("SELECT COUNT(*) as in_progress FROM complaints WHERE status='In Progress'")
# #     in_progress = cur.fetchone()['in_progress']
    
# #     cur.execute("SELECT COUNT(*) as resolved FROM complaints WHERE status='Resolved'")
# #     resolved = cur.fetchone()['resolved']
    
# #     # Get all complaints
# #     cur.execute("""
# #         SELECT c.*, u.gov_id_number, u.gov_id_type 
# #         FROM complaints c 
# #         LEFT JOIN users u ON c.user_id = u.id 
# #         ORDER BY c.id DESC
# #     """)
# #     complaints = cur.fetchall()
    
# #     cur.close()
    
# #     return render_template("admin.html", 
# #                          complaints=complaints,
# #                          total=total,
# #                          pending=pending,
# #                          in_progress=in_progress,
# #                          resolved=resolved)

# # @app.route("/update-status/<int:complaint_id>/<string:new_status>")
# # def update_status(complaint_id, new_status):
# #     if not session.get("admin_logged_in"):
# #         return redirect(url_for("admin_login"))
    
# #     conn = get_db()
# #     cur = conn.cursor()
# #     cur.execute("UPDATE complaints SET status=%s WHERE id=%s", (new_status, complaint_id))
# #     conn.commit()
# #     cur.close()
    
# #     return redirect(url_for("admin_dashboard"))

# # @app.route("/admin-logout")
# # def admin_logout():
# #     session.pop("admin_logged_in", None)
# #     session.pop("official_id", None)
# #     session.pop("official_name", None)
# #     return redirect(url_for("admin_login"))

# # # Run the Flask App
# # if __name__ == "__main__":
# #     print("🚀 Flask app is starting...")
# #     try:
# #         app.run(debug=True, host='0.0.0.0', port=5000)
# #     except Exception as e:
# #         print(f"❌ Error starting Flask app: {e}")
# #         import traceback
# #         traceback.print_exc()
#         # input("Press Enter to exit...")

# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from werkzeug.security import generate_password_hash, check_password_hash
# from werkzeug.utils import secure_filename
# import os
# from datetime import datetime

# app = Flask(__name__)
# app.secret_key = "supersecretkey"
# app.config['UPLOAD_FOLDER'] = 'static/uploads'
# app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

# # Ensure upload directory exists
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# # Mock user data for testing (since no database)
# users = {
#     "test_user": {
#         "password_hash": generate_password_hash("password123"),
#         "name": "Test User",
#         "locality": "Test Locality"
#     }
# }

# # Mock complaints data
# complaints = []

# # Mock officials data
# officials = {
#     "OFFICIAL_001": {
#         "password_hash": generate_password_hash("password123"),
#         "name": "Admin Officer",
#         "department": "Administration"
#     }
# }

# # ---------------- ROUTES ----------------

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/complaint")
# def complaint_form():
#     if "user_id" not in session:
#         return redirect(url_for("userlogin"))
#     return render_template("complaint.html", user=session["user_name"])

# @app.route("/submit-complaint", methods=["POST"])
# def submit_complaint():
#     if "user_id" not in session:
#         return redirect(url_for("userlogin"))
    
#     try:
#         name = request.form.get("name")
#         email = request.form.get("email")
#         category = request.form.get("category")
#         complaint_text = request.form.get("complaint")
#         locality = request.form.get("locality")
        
#         # Handle file upload
#         evidence_filename = None
#         if 'evidence' in request.files:
#             file = request.files['evidence']
#             if file and file.filename != '':
#                 filename = secure_filename(file.filename)
#                 evidence_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
#                 file.save(os.path.join(app.config['UPLOAD_FOLDER'], evidence_filename))

#         # Store complaint in memory (instead of database)
#         complaint_id = len(complaints) + 1
#         complaints.append({
#             "id": complaint_id,
#             "user_id": session["user_id"],
#             "name": name,
#             "email": email,
#             "category": category,
#             "complaint": complaint_text,
#             "locality": locality,
#             "evidence_filename": evidence_filename,
#             "status": "Pending",
#             "upvotes": 0,
#             "created_at": datetime.now()
#         })
        
#         flash("Complaint submitted successfully!", "success")
#         return redirect(url_for("dashboard"))
    
#     except Exception as e:
#         flash(f"Error submitting complaint: {str(e)}", "error")
#         return redirect(url_for("complaint_form"))

# @app.route("/dashboard")
# def dashboard():
#     if "user_id" not in session:
#         return redirect(url_for("userlogin"))
    
#     user_id = session.get("user_id")
#     user_locality = session.get("locality", "Test Locality")
    
#     # Get user's complaints from memory
#     user_complaints = [c for c in complaints if c.get("user_id") == user_id]
    
#     # Get locality complaints from memory
#     locality_complaints = [c for c in complaints if c.get("locality") == user_locality]

#     return render_template("dashboard.html", 
#                          user_complaints=user_complaints, 
#                          locality_complaints=locality_complaints, 
#                          locality=user_locality)

# @app.route("/upvote/<int:complaint_id>")
# def upvote(complaint_id):
#     if "user_id" not in session:
#         return redirect(url_for("userlogin"))
    
#     # Find and upvote the complaint
#     for complaint in complaints:
#         if complaint["id"] == complaint_id:
#             complaint["upvotes"] = complaint.get("upvotes", 0) + 1
#             break
    
#     return redirect(url_for("dashboard"))

# @app.route("/delete-complaint/<int:complaint_id>")
# def delete_complaint(complaint_id):
#     if "user_id" not in session:
#         return redirect(url_for("userlogin"))
    
#     # Find and remove the complaint
#     global complaints
#     complaints = [c for c in complaints if c["id"] != complaint_id]
    
#     return redirect(url_for("dashboard"))

# # ------------- Authentication Routes -------------

# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         gov_id_type = request.form.get("gov_id_type")
#         gov_id_number = request.form.get("gov_id_number")
#         name = request.form.get("name")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         locality = request.form.get("locality")

#         # Store user in memory (instead of database)
#         users[gov_id_number] = {
#             "password_hash": generate_password_hash(password),
#             "name": name,
#             "locality": locality
#         }
        
#         flash("Registration successful! Please login.", "success")
#         return redirect(url_for("userlogin"))
    
#     return render_template("register.html")

# @app.route("/userlogin", methods=["GET", "POST"])
# def userlogin():
#     if request.method == "POST":
#         gov_id_number = request.form.get("gov_id_number")
#         password = request.form.get("password")

#         user = users.get(gov_id_number)
        
#         if user and check_password_hash(user["password_hash"], password):
#             session["user_id"] = gov_id_number
#             session["user_name"] = user["name"]
#             session["locality"] = user["locality"]
#             return redirect(url_for("dashboard"))
#         else:
#             return render_template("userlogin.html", error="Invalid ID or Password")

#     return render_template("userlogin.html")

# @app.route("/logout-user")
# def logout_user():
#     session.pop("user_id", None)
#     session.pop("user_name", None)
#     session.pop("locality", None)
#     return redirect(url_for("index"))

# # ------------- Admin Routes -------------

# @app.route("/admin-login", methods=["GET", "POST"])
# def admin_login():
#     if request.method == "POST":
#         official_id = request.form.get("official_id")
#         password = request.form.get("password")

#         official = officials.get(official_id)
        
#         if official and check_password_hash(official["password_hash"], password):
#             session["admin_logged_in"] = True
#             session["official_id"] = official_id
#             session["official_name"] = official["name"]
#             return redirect(url_for("admin_dashboard"))
        
#         return render_template("adminlogin.html", error="Invalid Official ID or Password")
    
#     return render_template("adminlogin.html")

# @app.route("/admin")
# def admin_dashboard():
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin_login"))

#     # Calculate stats from memory
#     total = len(complaints)
#     pending = len([c for c in complaints if c.get("status") == "Pending"])
#     in_progress = len([c for c in complaints if c.get("status") == "In Progress"])
#     resolved = len([c for c in complaints if c.get("status") == "Resolved"])
    
#     return render_template("admin.html", 
#                          complaints=complaints,
#                          total=total,
#                          pending=pending,
#                          in_progress=in_progress,
#                          resolved=resolved)

# @app.route("/update-status/<int:complaint_id>/<string:new_status>")
# def update_status(complaint_id, new_status):
#     if not session.get("admin_logged_in"):
#         return redirect(url_for("admin_login"))
    
#     # Update complaint status in memory
#     for complaint in complaints:
#         if complaint["id"] == complaint_id:
#             complaint["status"] = new_status
#             break
    
#     return redirect(url_for("admin_dashboard"))

# @app.route("/admin-logout")
# def admin_logout():
#     session.pop("admin_logged_in", None)
#     session.pop("official_id", None)
#     session.pop("official_name", None)
#     return redirect(url_for("admin_login"))



# # Run the Flask App
# if __name__ == "__main__":
#     print("🚀 Flask app is starting...")
#     print("💡 Using in-memory storage (no database)")
#     try:
#         app.run(debug=True, host='0.0.0.0', port=5000)
#     except Exception as e:
#         print(f"❌ Error starting Flask app: {e}")
#         import traceback
#         traceback.print_exc()











from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit
app.config['DATABASE'] = 'myidealcity.db'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------------- DATABASE FUNCTIONS ----------------

def get_db():
    """Get database connection"""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row  # This enables column access by name
    return db

def init_db():
    """Initialize the database with tables"""
    db = get_db()
    cursor = db.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gov_id_type TEXT NOT NULL,
            gov_id_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            locality TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create complaints table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            category TEXT NOT NULL,
            complaint TEXT NOT NULL,
            locality TEXT NOT NULL,
            evidence_filename TEXT,
            status TEXT DEFAULT 'Pending',
            upvotes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create officials table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS officials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            official_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            department TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default admin if not exists
    cursor.execute("SELECT * FROM officials WHERE official_id = ?", ('OFFICIAL_001',))
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO officials (official_id, name, password_hash, department)
            VALUES (?, ?, ?, ?)
        ''', ('OFFICIAL_001', 'Admin Officer', generate_password_hash('password123'), 'Administration'))
    
    db.commit()
    db.close()
    print("✅ Database initialized successfully!")

# Initialize database when app starts
init_db()

# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/complaint")
def complaint_form():
    if "user_id" not in session:
        flash("Please login to file a complaint", "error")
        return redirect(url_for("userlogin"))
    return render_template("complaint.html")

@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():
    if "user_id" not in session:
        flash("Please login to file a complaint", "error")
        return redirect(url_for("userlogin"))
    
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        category = request.form.get("category")
        complaint_text = request.form.get("complaint")
        locality = request.form.get("locality")
        
        # Handle file upload
        evidence_filename = None
        if 'evidence' in request.files:
            file = request.files['evidence']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                evidence_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], evidence_filename))

        # Insert into database
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO complaints (user_id, name, email, category, complaint, locality, evidence_filename, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session["user_id"], name, email, category, complaint_text, locality, evidence_filename, "Pending"))
        db.commit()
        db.close()
        
        flash("Complaint submitted successfully!", "success")
        return redirect(url_for("dashboard"))
    
    except Exception as e:
        flash(f"Error submitting complaint: {str(e)}", "error")
        return redirect(url_for("complaint_form"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login to view dashboard", "error")
        return redirect(url_for("userlogin"))
    
    user_id = session.get("user_id")
    user_locality = session.get("locality", "")

    db = get_db()
    cursor = db.cursor()

    # Get user's complaints
    cursor.execute('''
        SELECT id, category, complaint, status, upvotes, locality, created_at 
        FROM complaints 
        WHERE user_id = ? 
        ORDER BY id DESC
    ''', (user_id,))
    user_complaints = [dict(row) for row in cursor.fetchall()]

    # Get locality complaints for upvoting
    cursor.execute('''
        SELECT id, category, complaint, status, upvotes, locality, created_at
        FROM complaints 
        WHERE locality = ? 
        ORDER BY id DESC
    ''', (user_locality,))
    locality_complaints = [dict(row) for row in cursor.fetchall()]
    
    db.close()

    return render_template("dashboard.html", 
                         user_complaints=user_complaints, 
                         locality_complaints=locality_complaints, 
                         locality=user_locality)

@app.route("/upvote/<int:complaint_id>")
def upvote(complaint_id):
    if "user_id" not in session:
        flash("Please login to upvote", "error")
        return redirect(url_for("userlogin"))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE complaints SET upvotes = upvotes + 1 WHERE id = ?", (complaint_id,))
    db.commit()
    db.close()
    
    flash("Upvoted successfully!", "success")
    return redirect(url_for("dashboard"))

@app.route("/delete-complaint/<int:complaint_id>")
def delete_complaint(complaint_id):
    if "user_id" not in session:
        flash("Please login to delete complaint", "error")
        return redirect(url_for("userlogin"))
    
    db = get_db()
    cursor = db.cursor()
    
    # Verify the complaint belongs to the user
    cursor.execute("SELECT user_id, evidence_filename FROM complaints WHERE id = ?", (complaint_id,))
    result = cursor.fetchone()
    
    if result and result['user_id'] == session["user_id"]:
        evidence_file = result['evidence_filename']
        
        # Delete the complaint
        cursor.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
        db.commit()
        
        # Delete evidence file if exists
        if evidence_file:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], evidence_file))
            except:
                pass  # Silently fail if file doesn't exist
        
        flash("Complaint deleted successfully!", "success")
    else:
        flash("You can only delete your own complaints!", "error")
    
    db.close()
    return redirect(url_for("dashboard"))

# ------------- Authentication Routes -------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        gov_id_type = request.form.get("gov_id_type")
        gov_id_number = request.form.get("gov_id_number")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        locality = request.form.get("locality")

        hashed_pw = generate_password_hash(password)

        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                INSERT INTO users (gov_id_type, gov_id_number, name, email, password, locality)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (gov_id_type, gov_id_number, name, email, hashed_pw, locality))
            db.commit()
            db.close()
            
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("userlogin"))
        
        except sqlite3.IntegrityError:
            flash("Government ID or Email already exists!", "error")
            return render_template("register.html")
    
    return render_template("register.html")

@app.route("/userlogin", methods=["GET", "POST"])
def userlogin():
    if request.method == "POST":
        gov_id_number = request.form.get("gov_id_number")
        password = request.form.get("password")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE gov_id_number = ?", (gov_id_number,))
        user = cursor.fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = gov_id_number
            session["user_name"] = user["name"]
            session["locality"] = user["locality"]
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            return render_template("userlogin.html", error="Invalid ID or Password")

    return render_template("userlogin.html")

@app.route("/logout-user")
def logout_user():
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("locality", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("index"))

# ------------- Admin Routes -------------

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        official_id = request.form.get("official_id")
        password = request.form.get("password")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM officials WHERE official_id = ? AND is_active = 1", (official_id,))
        official = cursor.fetchone()
        db.close()

        if official and check_password_hash(official["password_hash"], password):
            session["admin_logged_in"] = True
            session["official_id"] = official["official_id"]
            session["official_name"] = official["name"]
            flash(f"Welcome, {official['name']}!", "success")
            return redirect(url_for("admin_dashboard"))
        
        return render_template("adminlogin.html", error="Invalid Official ID or Password")
    
    return render_template("adminlogin.html")

@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        flash("Please login as admin to access this page", "error")
        return redirect(url_for("admin_login"))

    db = get_db()
    cursor = db.cursor()
    
    # Get stats
    cursor.execute("SELECT COUNT(*) as total FROM complaints")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as pending FROM complaints WHERE status='Pending'")
    pending = cursor.fetchone()['pending']
    
    cursor.execute("SELECT COUNT(*) as in_progress FROM complaints WHERE status='In Progress'")
    in_progress = cursor.fetchone()['in_progress']
    
    cursor.execute("SELECT COUNT(*) as resolved FROM complaints WHERE status='Resolved'")
    resolved = cursor.fetchone()['resolved']
    
    # Get all complaints
    cursor.execute('''
        SELECT c.*, u.gov_id_number, u.gov_id_type 
        FROM complaints c 
        LEFT JOIN users u ON c.user_id = u.gov_id_number 
        ORDER BY c.id DESC
    ''')
    complaints = [dict(row) for row in cursor.fetchall()]
    
    db.close()
    
    return render_template("admin.html", 
                         complaints=complaints,
                         total=total,
                         pending=pending,
                         in_progress=in_progress,
                         resolved=resolved)

@app.route("/update-status/<int:complaint_id>/<string:new_status>")
def update_status(complaint_id, new_status):
    if not session.get("admin_logged_in"):
        flash("Please login as admin", "error")
        return redirect(url_for("admin_login"))
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE complaints SET status = ? WHERE id = ?", (new_status, complaint_id))
    db.commit()
    db.close()
    
    flash(f"Complaint status updated to {new_status}!", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin-logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("official_id", None)
    session.pop("official_name", None)
    flash("Admin logged out successfully!", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin/complaint/<int:complaint_id>")
def complaint_details(complaint_id):
    if not session.get("admin_logged_in"):
        flash("Please login as admin", "error")
        return redirect(url_for("admin_login"))
    
    db = get_db()
    cursor = db.cursor()
    
    # Get complaint details with user info
    cursor.execute('''
        SELECT c.*, u.gov_id_number, u.gov_id_type 
        FROM complaints c 
        LEFT JOIN users u ON c.user_id = u.gov_id_number 
        WHERE c.id = ?
    ''', (complaint_id,))
    
    complaint = cursor.fetchone()
    db.close()
    
    if not complaint:
        flash("Complaint not found!", "error")
        return redirect(url_for("admin_dashboard"))
    
    # Convert to dictionary
    complaint = dict(complaint)
    
    return render_template("complaint_details.html", complaint=complaint)



# Run the Flask App
if __name__ == "__main__":
    print("🚀 Flask app is starting with SQLite database...")
    print("✅ Database file: myidealcity.db")
    print("✅ Default Admin - ID: OFFICIAL_001, Password: password123")
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        import traceback
        traceback.print_exc()