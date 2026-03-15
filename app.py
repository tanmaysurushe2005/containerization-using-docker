# pyright: reportCallIssue=false
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash, check_password_hash
import socket
import datetime
import random
import os
import time
import re
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "student-portal-dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "mysql+pymysql://student_user:student_pass@localhost:3306/student_portal"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

INITIAL_PASSWORD_SUFFIX = os.environ.get("INITIAL_PASSWORD_SUFFIX", "@vu2026")
DEFAULT_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@12345")
DB_INIT_RETRIES = int(os.environ.get("DB_INIT_RETRIES", "20"))
DB_INIT_DELAY_SECONDS = float(os.environ.get("DB_INIT_DELAY_SECONDS", "2"))
PASSWORD_MIN_LENGTH = int(os.environ.get("PASSWORD_MIN_LENGTH", "8"))
STUDENT_MAX_FAILED_LOGIN_ATTEMPTS = int(
    os.environ.get("STUDENT_MAX_FAILED_LOGIN_ATTEMPTS", os.environ.get("MAX_FAILED_LOGIN_ATTEMPTS", "5"))
)
STUDENT_LOCKOUT_MINUTES = int(
    os.environ.get("STUDENT_LOCKOUT_MINUTES", os.environ.get("LOCKOUT_MINUTES", "15"))
)
ADMIN_MAX_FAILED_LOGIN_ATTEMPTS = int(
    os.environ.get("ADMIN_MAX_FAILED_LOGIN_ATTEMPTS", os.environ.get("MAX_FAILED_LOGIN_ATTEMPTS", "5"))
)
ADMIN_LOCKOUT_MINUTES = int(
    os.environ.get("ADMIN_LOCKOUT_MINUTES", os.environ.get("LOCKOUT_MINUTES", "15"))
)

# Simulated student database
students_db = {
    "S2401": {"name": "Aarav Sharma",     "roll": "S2401", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 88, "Probablity and Statistics": 91, "Design and Analysis of Algorithms": 85, "Machine Learning": 79, "Design Thinking": 92, "Database Management System": 87}},
    "S2402": {"name": "Priya Patel",      "roll": "S2402", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 76, "Probablity and Statistics": 83, "Design and Analysis of Algorithms": 90, "Machine Learning": 88, "Design Thinking": 74, "Database Management System": 81}},
    "S2403": {"name": "Rohit Verma",      "roll": "S2403", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 62, "Probablity and Statistics": 70, "Design and Analysis of Algorithms": 68, "Machine Learning": 75, "Design Thinking": 80, "Database Management System": 65}},
    "S2404": {"name": "Sneha Joshi",      "roll": "S2404", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 95, "Probablity and Statistics": 98, "Design and Analysis of Algorithms": 92, "Machine Learning": 94, "Design Thinking": 96, "Database Management System": 91}},
    "S2405": {"name": "Karan Mehta",      "roll": "S2405", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 71, "Probablity and Statistics": 68, "Design and Analysis of Algorithms": 74, "Machine Learning": 80, "Design Thinking": 66, "Database Management System": 72}},
    "S2406": {"name": "Anjali Singh",     "roll": "S2406", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 84, "Probablity and Statistics": 79, "Design and Analysis of Algorithms": 88, "Machine Learning": 82, "Design Thinking": 77, "Database Management System": 83}},
    "S2407": {"name": "Vikram Nair",      "roll": "S2407", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 55, "Probablity and Statistics": 61, "Design and Analysis of Algorithms": 58, "Machine Learning": 63, "Design Thinking": 70, "Database Management System": 60}},
    "S2408": {"name": "Divya Reddy",      "roll": "S2408", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 90, "Probablity and Statistics": 87, "Design and Analysis of Algorithms": 93, "Machine Learning": 85, "Design Thinking": 89, "Database Management System": 94}},
    "S2409": {"name": "Arjun Kulkarni",   "roll": "S2409", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 74, "Probablity and Statistics": 69, "Design and Analysis of Algorithms": 77, "Machine Learning": 72, "Design Thinking": 81, "Database Management System": 68}},
    "S2410": {"name": "Nisha Desai",      "roll": "S2410", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 83, "Probablity and Statistics": 76, "Design and Analysis of Algorithms": 80, "Machine Learning": 91, "Design Thinking": 85, "Database Management System": 78}},
    "S2411": {"name": "Rajan Iyer",       "roll": "S2411", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 59, "Probablity and Statistics": 64, "Design and Analysis of Algorithms": 61, "Machine Learning": 57, "Design Thinking": 66, "Database Management System": 62}},
    "S2412": {"name": "Pooja Mishra",     "roll": "S2412", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 91, "Probablity and Statistics": 86, "Design and Analysis of Algorithms": 94, "Machine Learning": 89, "Design Thinking": 93, "Database Management System": 88}},
    "S2413": {"name": "Sameer Khan",      "roll": "S2413", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 67, "Probablity and Statistics": 72, "Design and Analysis of Algorithms": 65, "Machine Learning": 70, "Design Thinking": 74, "Database Management System": 69}},
    "S2414": {"name": "Tanvi Bhatt",      "roll": "S2414", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 78, "Probablity and Statistics": 82, "Design and Analysis of Algorithms": 75, "Machine Learning": 84, "Design Thinking": 79, "Database Management System": 86}},
    "S2415": {"name": "Harsh Tiwari",     "roll": "S2415", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 53, "Probablity and Statistics": 58, "Design and Analysis of Algorithms": 47, "Machine Learning": 55, "Design Thinking": 61, "Database Management System": 50}},
    "S2416": {"name": "Meera Pillai",     "roll": "S2416", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 86, "Probablity and Statistics": 90, "Design and Analysis of Algorithms": 83, "Machine Learning": 87, "Design Thinking": 91, "Database Management System": 85}},
    "S2417": {"name": "Nikhil Rao",       "roll": "S2417", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 70, "Probablity and Statistics": 65, "Design and Analysis of Algorithms": 73, "Machine Learning": 68, "Design Thinking": 76, "Database Management System": 71}},
    "S2418": {"name": "Kavya Menon",      "roll": "S2418", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 92, "Probablity and Statistics": 88, "Design and Analysis of Algorithms": 96, "Machine Learning": 90, "Design Thinking": 87, "Database Management System": 93}},
    "S2419": {"name": "Aditya Jain",      "roll": "S2419", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 64, "Probablity and Statistics": 71, "Design and Analysis of Algorithms": 67, "Machine Learning": 73, "Design Thinking": 69, "Database Management System": 66}},
    "S2420": {"name": "Shruti Gupta",     "roll": "S2420", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 80, "Probablity and Statistics": 77, "Design and Analysis of Algorithms": 84, "Machine Learning": 78, "Design Thinking": 82, "Database Management System": 79}},
    "S2421": {"name": "Vivek Chandra",    "roll": "S2421", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 57, "Probablity and Statistics": 62, "Design and Analysis of Algorithms": 54, "Machine Learning": 60, "Design Thinking": 58, "Database Management System": 63}},
    "S2422": {"name": "Isha Saxena",      "roll": "S2422", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 89, "Probablity and Statistics": 84, "Design and Analysis of Algorithms": 87, "Machine Learning": 92, "Design Thinking": 86, "Database Management System": 90}},
    "S2423": {"name": "Manish Dubey",     "roll": "S2423", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 66, "Probablity and Statistics": 60, "Design and Analysis of Algorithms": 69, "Machine Learning": 64, "Design Thinking": 72, "Database Management System": 67}},
    "S2424": {"name": "Ritika Bose",      "roll": "S2424", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 77, "Probablity and Statistics": 81, "Design and Analysis of Algorithms": 79, "Machine Learning": 75, "Design Thinking": 83, "Database Management System": 76}},
    "S2425": {"name": "Suresh Nambiar",   "roll": "S2425", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 48, "Probablity and Statistics": 53, "Design and Analysis of Algorithms": 45, "Machine Learning": 51, "Design Thinking": 56, "Database Management System": 49}},
    "S2426": {"name": "Deepa Krishnan",   "roll": "S2426", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 93, "Probablity and Statistics": 89, "Design and Analysis of Algorithms": 91, "Machine Learning": 95, "Design Thinking": 88, "Database Management System": 92}},
    "S2427": {"name": "Gaurav Shukla",    "roll": "S2427", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 72, "Probablity and Statistics": 67, "Design and Analysis of Algorithms": 76, "Machine Learning": 70, "Design Thinking": 65, "Database Management System": 73}},
    "S2428": {"name": "Poonam Thakur",    "roll": "S2428", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 85, "Probablity and Statistics": 78, "Design and Analysis of Algorithms": 82, "Machine Learning": 86, "Design Thinking": 80, "Database Management System": 84}},
    "S2429": {"name": "Rahul Pandey",     "roll": "S2429", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 61, "Probablity and Statistics": 66, "Design and Analysis of Algorithms": 63, "Machine Learning": 58, "Design Thinking": 67, "Database Management System": 64}},
    "S2430": {"name": "Swati Malhotra",   "roll": "S2430", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 87, "Probablity and Statistics": 92, "Design and Analysis of Algorithms": 85, "Machine Learning": 88, "Design Thinking": 94, "Database Management System": 89}},
    "S2431": {"name": "Abhishek Das",     "roll": "S2431", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 69, "Probablity and Statistics": 74, "Design and Analysis of Algorithms": 71, "Machine Learning": 77, "Design Thinking": 63, "Database Management System": 70}},
    "S2432": {"name": "Neha Agarwal",     "roll": "S2432", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 82, "Probablity and Statistics": 85, "Design and Analysis of Algorithms": 88, "Machine Learning": 81, "Design Thinking": 84, "Database Management System": 87}},
    "S2433": {"name": "Siddharth Roy",    "roll": "S2433", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 56, "Probablity and Statistics": 50, "Design and Analysis of Algorithms": 59, "Machine Learning": 54, "Design Thinking": 62, "Database Management System": 57}},
    "S2434": {"name": "Ananya Chatterjee","roll": "S2434", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 94, "Probablity and Statistics": 91, "Design and Analysis of Algorithms": 97, "Machine Learning": 93, "Design Thinking": 90, "Database Management System": 95}},
    "S2435": {"name": "Pranav Hegde",     "roll": "S2435", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 75, "Probablity and Statistics": 69, "Design and Analysis of Algorithms": 72, "Machine Learning": 78, "Design Thinking": 68, "Database Management System": 74}},
    "S2436": {"name": "Simran Kaur",      "roll": "S2436", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 81, "Probablity and Statistics": 86, "Design and Analysis of Algorithms": 78, "Machine Learning": 83, "Design Thinking": 88, "Database Management System": 80}},
    "S2437": {"name": "Tarun Bajaj",      "roll": "S2437", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 63, "Probablity and Statistics": 68, "Design and Analysis of Algorithms": 60, "Machine Learning": 66, "Design Thinking": 71, "Database Management System": 65}},
    "S2438": {"name": "Varsha Nair",      "roll": "S2438", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 88, "Probablity and Statistics": 83, "Design and Analysis of Algorithms": 91, "Machine Learning": 86, "Design Thinking": 85, "Database Management System": 89}},
    "S2439": {"name": "Yash Patil",       "roll": "S2439", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 52, "Probablity and Statistics": 57, "Design and Analysis of Algorithms": 49, "Machine Learning": 55, "Design Thinking": 60, "Database Management System": 53}},
    "S2440": {"name": "Zara Sheikh",      "roll": "S2440", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 79, "Probablity and Statistics": 84, "Design and Analysis of Algorithms": 76, "Machine Learning": 81, "Design Thinking": 87, "Database Management System": 82}},
    "S2441": {"name": "Akash Tripathi",   "roll": "S2441", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 68, "Probablity and Statistics": 63, "Design and Analysis of Algorithms": 71, "Machine Learning": 67, "Design Thinking": 75, "Database Management System": 69}},
    "S2442": {"name": "Bhavna Joshi",     "roll": "S2442", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 96, "Probablity and Statistics": 93, "Design and Analysis of Algorithms": 89, "Machine Learning": 97, "Design Thinking": 92, "Database Management System": 94}},
    "S2443": {"name": "Chirag Vora",      "roll": "S2443", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 73, "Probablity and Statistics": 78, "Design and Analysis of Algorithms": 70, "Machine Learning": 76, "Design Thinking": 64, "Database Management System": 75}},
    "S2444": {"name": "Disha Kapoor",     "roll": "S2444", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 84, "Probablity and Statistics": 80, "Design and Analysis of Algorithms": 87, "Machine Learning": 83, "Design Thinking": 89, "Database Management System": 86}},
    "S2445": {"name": "Ekta Srivastava",  "roll": "S2445", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 58, "Probablity and Statistics": 54, "Design and Analysis of Algorithms": 62, "Machine Learning": 59, "Design Thinking": 65, "Database Management System": 61}},
    "S2446": {"name": "Farhan Ansari",    "roll": "S2446", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 77, "Probablity and Statistics": 73, "Design and Analysis of Algorithms": 80, "Machine Learning": 74, "Design Thinking": 78, "Database Management System": 76}},
    "S2447": {"name": "Gargi Banerjee",   "roll": "S2447", "branch": "Electronics & Comm",  "semester": "VI", "subjects": {"System Programming & Operating Systems": 65, "Probablity and Statistics": 70, "Design and Analysis of Algorithms": 67, "Machine Learning": 72, "Design Thinking": 61, "Database Management System": 68}},
    "S2448": {"name": "Hemant Solanki",   "roll": "S2448", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 90, "Probablity and Statistics": 87, "Design and Analysis of Algorithms": 84, "Machine Learning": 91, "Design Thinking": 88, "Database Management System": 92}},
    "S2449": {"name": "Ishita Mathur",    "roll": "S2449", "branch": "Information Tech",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 71, "Probablity and Statistics": 76, "Design and Analysis of Algorithms": 74, "Machine Learning": 69, "Design Thinking": 79, "Database Management System": 73}},
    "S2450": {"name": "Jayesh Pawar",     "roll": "S2450", "branch": "Computer Science",    "semester": "VI", "subjects": {"System Programming & Operating Systems": 83, "Probablity and Statistics": 88, "Design and Analysis of Algorithms": 81, "Machine Learning": 85, "Design Thinking": 90, "Database Management System": 84}},
}


class StudentCredential(db.Model):
    __tablename__ = "student_credentials"

    roll_number = db.Column(db.String(20), primary_key=True)
    password_hash = db.Column(db.String(255), nullable=False)
    must_change_password = db.Column(db.Boolean, nullable=False, default=True)
    failed_login_attempts = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )


class AdminCredential(db.Model):
    __tablename__ = "admin_credentials"

    username = db.Column(db.String(80), primary_key=True)
    password_hash = db.Column(db.String(255), nullable=False)
    failed_login_attempts = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )


class AuthAuditLog(db.Model):
    __tablename__ = "auth_audit_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(db.String(80), nullable=False)
    account_role = db.Column(db.String(20), nullable=False)
    event_type = db.Column(db.String(40), nullable=False)
    event_status = db.Column(db.String(20), nullable=False)
    ip_address = db.Column(db.String(64), nullable=False, default="unknown")
    user_agent = db.Column(db.String(255), nullable=False, default="unknown")
    details = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)


def seed_student_credentials():
    for roll in students_db:
        existing = StudentCredential.query.filter(StudentCredential.roll_number == roll).first()
        if existing:
            continue
        initial_password = f"{roll.lower()}{INITIAL_PASSWORD_SUFFIX}"
        credential = StudentCredential()
        credential.roll_number = roll
        credential.password_hash = generate_password_hash(initial_password)
        credential.must_change_password = True
        credential.failed_login_attempts = 0
        credential.locked_until = None
        db.session.add(credential)


def seed_admin_credentials():
    existing = AdminCredential.query.filter(AdminCredential.username == DEFAULT_ADMIN_USERNAME).first()
    if existing:
        return

    admin = AdminCredential()
    admin.username = DEFAULT_ADMIN_USERNAME
    admin.password_hash = generate_password_hash(DEFAULT_ADMIN_PASSWORD)
    admin.failed_login_attempts = 0
    admin.locked_until = None
    db.session.add(admin)


def ensure_auth_lockout_columns():
    inspector = inspect(db.engine)

    table_columns = {
        "student_credentials": {
            col["name"] for col in inspector.get_columns("student_credentials")
        },
        "admin_credentials": {
            col["name"] for col in inspector.get_columns("admin_credentials")
        },
    }

    if "failed_login_attempts" not in table_columns["student_credentials"]:
        db.session.execute(
            text("ALTER TABLE student_credentials ADD COLUMN failed_login_attempts INT NOT NULL DEFAULT 0")
        )
    if "locked_until" not in table_columns["student_credentials"]:
        db.session.execute(
            text("ALTER TABLE student_credentials ADD COLUMN locked_until DATETIME NULL")
        )
    if "failed_login_attempts" not in table_columns["admin_credentials"]:
        db.session.execute(
            text("ALTER TABLE admin_credentials ADD COLUMN failed_login_attempts INT NOT NULL DEFAULT 0")
        )
    if "locked_until" not in table_columns["admin_credentials"]:
        db.session.execute(
            text("ALTER TABLE admin_credentials ADD COLUMN locked_until DATETIME NULL")
        )


def initialize_database_with_retry():
    for attempt in range(1, DB_INIT_RETRIES + 1):
        try:
            db.create_all()
            ensure_auth_lockout_columns()
            seed_student_credentials()
            seed_admin_credentials()
            db.session.commit()
            return
        except OperationalError:
            db.session.rollback()
            if attempt == DB_INIT_RETRIES:
                raise
            print(f"Database not ready (attempt {attempt}/{DB_INIT_RETRIES}). Retrying...")
            time.sleep(DB_INIT_DELAY_SECONDS)


def get_lockout_policy(role):
    if role == "admin":
        return ADMIN_MAX_FAILED_LOGIN_ATTEMPTS, ADMIN_LOCKOUT_MINUTES
    return STUDENT_MAX_FAILED_LOGIN_ATTEMPTS, STUDENT_LOCKOUT_MINUTES


def get_request_context():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    ip = (forwarded_for.split(",")[0].strip() if forwarded_for else "") or request.remote_addr or "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")
    return {
        "ip_address": ip[:64],
        "user_agent": user_agent[:255],
    }


def write_auth_audit(account_id, role, event_type, status, details, context_data=None):
    ctx = context_data or {"ip_address": "unknown", "user_agent": "unknown"}
    audit = AuthAuditLog()
    audit.account_id = account_id or "unknown"
    audit.account_role = role
    audit.event_type = event_type
    audit.event_status = status
    audit.ip_address = (ctx.get("ip_address") or "unknown")[:64]
    audit.user_agent = (ctx.get("user_agent") or "unknown")[:255]
    audit.details = details
    db.session.add(audit)
    db.session.commit()


def validate_password_policy(password):
    if len(password) < PASSWORD_MIN_LENGTH:
        return f"Password must be at least {PASSWORD_MIN_LENGTH} characters."
    if not re.search(r"[A-Z]", password):
        return "Password must include at least one uppercase letter."
    if not re.search(r"[0-9]", password):
        return "Password must include at least one number."
    if not re.search(r"[^A-Za-z0-9]", password):
        return "Password must include at least one symbol."
    return None


def account_lock_message(locked_until):
    if not locked_until:
        return None

    now = datetime.datetime.utcnow()
    if locked_until <= now:
        return None

    remaining_seconds = int((locked_until - now).total_seconds())
    remaining_minutes = (remaining_seconds // 60) + (1 if remaining_seconds % 60 else 0)
    return f"Account is locked due to repeated failed attempts. Try again in {remaining_minutes} minute(s)."


def reset_lock_state(credential):
    credential.failed_login_attempts = 0
    credential.locked_until = None


def register_failed_login_attempt(credential, role, account_id, context_data):
    max_attempts, lockout_minutes = get_lockout_policy(role)
    now = datetime.datetime.utcnow()
    credential.failed_login_attempts = (credential.failed_login_attempts or 0) + 1

    if credential.failed_login_attempts >= max_attempts:
        credential.failed_login_attempts = 0
        credential.locked_until = now + datetime.timedelta(minutes=lockout_minutes)
        db.session.commit()
        write_auth_audit(
            account_id=account_id,
            role=role,
            event_type="login_lockout",
            status="failure",
            details=f"Account locked after {max_attempts} failed login attempts for {lockout_minutes} minutes.",
            context_data=context_data,
        )
        return f"Too many failed attempts. Account locked for {lockout_minutes} minute(s)."

    remaining = max_attempts - credential.failed_login_attempts
    db.session.commit()
    write_auth_audit(
        account_id=account_id,
        role=role,
        event_type="login_failed",
        status="failure",
        details=f"Invalid password. {remaining} attempt(s) remaining before lockout.",
        context_data=context_data,
    )
    return f"Invalid password. {remaining} attempt(s) remaining before lockout."

def get_grade(marks):
    if marks >= 90: return "O", "Outstanding"
    elif marks >= 80: return "A+", "Excellent"
    elif marks >= 70: return "A", "Very Good"
    elif marks >= 60: return "B+", "Good"
    elif marks >= 50: return "B", "Average"
    else: return "F", "Fail"

def get_result_summary(subjects):
    total = sum(subjects.values())
    avg = total / len(subjects)
    passed = all(m >= 40 for m in subjects.values())
    grade, _ = get_grade(avg)
    return {
        "total": total,
        "avg": round(avg, 2),
        "passed": passed,
        "grade": grade,
        "percentage": round(avg, 2)
    }


def student_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if session.get("auth_role") != "student" or "student_roll" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if session.get("auth_role") != "admin" or "admin_username" not in session:
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def get_logged_in_student():
    roll = session.get("student_roll")
    if not isinstance(roll, str) or not roll:
        return None, None
    student = students_db.get(roll)
    if not student:
        session.clear()
        return None, None
    return roll, student


def get_logged_in_admin():
    username = session.get("admin_username")
    if not isinstance(username, str) or not username:
        return None
    return username


def validate_student_login(roll, password, context_data):
    credential = StudentCredential.query.filter(StudentCredential.roll_number == roll).first()
    if not credential:
        write_auth_audit(
            account_id=roll,
            role="student",
            event_type="login_failed",
            status="failure",
            details="Student credential record not found.",
            context_data=context_data,
        )
        return None, "Student credential record not found. Contact admin."

    lock_msg = account_lock_message(credential.locked_until)
    if lock_msg:
        write_auth_audit(
            account_id=roll,
            role="student",
            event_type="login_blocked",
            status="failure",
            details=lock_msg,
            context_data=context_data,
        )
        return None, lock_msg

    if credential.locked_until:
        reset_lock_state(credential)
        db.session.commit()
        write_auth_audit(
            account_id=roll,
            role="student",
            event_type="lockout_cleared",
            status="success",
            details="Lockout expired and account was unlocked.",
            context_data=context_data,
        )

    if not check_password_hash(credential.password_hash, password):
        return None, register_failed_login_attempt(credential, "student", roll, context_data)

    if credential.failed_login_attempts or credential.locked_until:
        reset_lock_state(credential)
        db.session.commit()

    write_auth_audit(
        account_id=roll,
        role="student",
        event_type="login_success",
        status="success",
        details="Student login successful.",
        context_data=context_data,
    )
    return credential, None


def validate_admin_login(username, password, context_data):
    credential = AdminCredential.query.filter(AdminCredential.username == username).first()
    if not credential:
        write_auth_audit(
            account_id=username,
            role="admin",
            event_type="login_failed",
            status="failure",
            details="Invalid admin username.",
            context_data=context_data,
        )
        return None, "Invalid admin credentials."

    lock_msg = account_lock_message(credential.locked_until)
    if lock_msg:
        write_auth_audit(
            account_id=username,
            role="admin",
            event_type="login_blocked",
            status="failure",
            details=lock_msg,
            context_data=context_data,
        )
        return None, lock_msg

    if credential.locked_until:
        reset_lock_state(credential)
        db.session.commit()
        write_auth_audit(
            account_id=username,
            role="admin",
            event_type="lockout_cleared",
            status="success",
            details="Lockout expired and account was unlocked.",
            context_data=context_data,
        )

    if not check_password_hash(credential.password_hash, password):
        return None, register_failed_login_attempt(credential, "admin", username, context_data)

    if credential.failed_login_attempts or credential.locked_until:
        reset_lock_state(credential)
        db.session.commit()

    write_auth_audit(
        account_id=username,
        role="admin",
        event_type="login_success",
        status="success",
        details="Admin login successful.",
        context_data=context_data,
    )
    return credential, None


@app.route('/')
def root_redirect():
    role = session.get("auth_role")
    if role == "student":
        return redirect(url_for('index'))
    if role == "admin":
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("auth_role") == "student" and request.method == 'GET':
        return redirect(url_for('index'))
    if session.get("auth_role") == "admin" and request.method == 'GET':
        return redirect(url_for('admin_dashboard'))

    error = None
    roll_hint = ""
    if request.method == 'POST':
        context_data = get_request_context()
        roll = request.form.get('roll_number', '').strip().upper()
        password = request.form.get('password', '').strip()
        student = students_db.get(roll)
        credential, auth_error = validate_student_login(roll, password, context_data)

        if not student:
            error = f"No student found with Roll Number: {roll}"
            roll_hint = roll
        elif not credential:
            error = auth_error or "Invalid password. Please check your credentials."
            roll_hint = roll
        else:
            session.clear()
            session['auth_role'] = 'student'
            session['student_roll'] = roll
            if credential.must_change_password:
                return redirect(url_for('change_password'))
            return redirect(url_for('index'))

    container_id = socket.gethostname()
    now = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")
    return render_template(
        'login.html',
        container_id=container_id,
        timestamp=now,
        error=error,
        roll_hint=roll_hint,
        password_suffix=INITIAL_PASSWORD_SUFFIX
    )


@app.route('/change-password', methods=['GET', 'POST'])
@student_required
def change_password():
    roll, student = get_logged_in_student()
    if not student or not roll:
        return redirect(url_for('login'))

    credential = StudentCredential.query.filter(StudentCredential.roll_number == roll).first()
    if not credential:
        session.clear()
        return redirect(url_for('login'))

    error = None
    if request.method == 'POST':
        context_data = get_request_context()
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        policy_error = validate_password_policy(new_password)

        if not check_password_hash(credential.password_hash, current_password):
            error = "Current password is incorrect."
            write_auth_audit(
                account_id=roll,
                role="student",
                event_type="password_change_failed",
                status="failure",
                details="Current password mismatch while changing password.",
                context_data=context_data,
            )
        elif policy_error:
            error = policy_error
            write_auth_audit(
                account_id=roll,
                role="student",
                event_type="password_change_failed",
                status="failure",
                details=policy_error,
                context_data=context_data,
            )
        elif new_password != confirm_password:
            error = "New password and confirm password do not match."
            write_auth_audit(
                account_id=roll,
                role="student",
                event_type="password_change_failed",
                status="failure",
                details="Password confirmation mismatch.",
                context_data=context_data,
            )
        else:
            credential.password_hash = generate_password_hash(new_password)
            credential.must_change_password = False
            db.session.commit()
            write_auth_audit(
                account_id=roll,
                role="student",
                event_type="password_change_success",
                status="success",
                details="Password changed successfully.",
                context_data=context_data,
            )
            return redirect(url_for('index'))

    container_id = socket.gethostname()
    now = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")
    return render_template(
        'change_password.html',
        student=student,
        container_id=container_id,
        timestamp=now,
        error=error,
    )


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get("auth_role") == "admin" and request.method == 'GET':
        return redirect(url_for('admin_dashboard'))
    if session.get("auth_role") == "student" and request.method == 'GET':
        return redirect(url_for('index'))

    error = None
    username_hint = ""
    if request.method == 'POST':
        context_data = get_request_context()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        credential, auth_error = validate_admin_login(username, password, context_data)

        if not credential:
            error = auth_error or "Invalid admin credentials."
            username_hint = username
        else:
            session.clear()
            session['auth_role'] = 'admin'
            session['admin_username'] = credential.username
            return redirect(url_for('admin_dashboard'))

    container_id = socket.gethostname()
    now = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")
    return render_template(
        'admin_login.html',
        container_id=container_id,
        timestamp=now,
        error=error,
        username_hint=username_hint,
    )


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    query = request.args.get('q', '').strip().lower()
    message = request.args.get('msg', '').strip()
    admin_username = get_logged_in_admin()

    credentials = {
        cred.roll_number: cred
        for cred in StudentCredential.query.order_by(StudentCredential.roll_number.asc()).all()
    }
    recent_audit_logs = AuthAuditLog.query.order_by(AuthAuditLog.created_at.desc()).limit(25).all()

    students = []
    for roll, student in students_db.items():
        if query and query not in roll.lower() and query not in student['name'].lower() and query not in student['branch'].lower():
            continue

        credential = credentials.get(roll)
        students.append(
            {
                "roll": roll,
                "name": student['name'],
                "branch": student['branch'],
                "semester": student['semester'],
                "password_hash": credential.password_hash if credential else "Not seeded",
                "must_change_password": credential.must_change_password if credential else True,
                "updated_at": credential.updated_at.strftime("%d %b %Y %I:%M %p") if credential and credential.updated_at else "N/A",
            }
        )

    container_id = socket.gethostname()
    now = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")
    return render_template(
        'admin_dashboard.html',
        students=students,
        audit_logs=recent_audit_logs,
        query=query,
        message=message,
        student_lockout_attempts=STUDENT_MAX_FAILED_LOGIN_ATTEMPTS,
        student_lockout_minutes=STUDENT_LOCKOUT_MINUTES,
        admin_lockout_attempts=ADMIN_MAX_FAILED_LOGIN_ATTEMPTS,
        admin_lockout_minutes=ADMIN_LOCKOUT_MINUTES,
        admin_username=admin_username,
        container_id=container_id,
        timestamp=now,
    )


@app.route('/admin/reset-password', methods=['POST'])
@admin_required
def admin_reset_password():
    context_data = get_request_context()
    roll = request.form.get('roll_number', '').strip().upper()
    new_password = request.form.get('new_password', '').strip()
    query = request.form.get('query', '').strip()

    if roll not in students_db:
        return redirect(url_for('admin_dashboard', q=query, msg=f"Unknown student roll number: {roll}"))

    policy_error = validate_password_policy(new_password)
    if policy_error:
        return redirect(url_for('admin_dashboard', q=query, msg=policy_error))

    credential = StudentCredential.query.filter(StudentCredential.roll_number == roll).first()
    if not credential:
        credential = StudentCredential()
        credential.roll_number = roll
        credential.password_hash = generate_password_hash(new_password)
        credential.must_change_password = True
        db.session.add(credential)
    else:
        credential.password_hash = generate_password_hash(new_password)
        credential.must_change_password = True

    db.session.commit()
    write_auth_audit(
        account_id=session.get('admin_username', 'admin'),
        role="admin",
        event_type="password_reset",
        status="success",
        details=f"Admin reset password for student {roll}.",
        context_data=context_data,
    )
    return redirect(url_for('admin_dashboard', q=query, msg=f"Password reset for {roll}. Student must change password after next login."))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@student_required
def index():
    _, student = get_logged_in_student()
    if not student:
        return redirect(url_for('login'))

    credential = StudentCredential.query.filter(StudentCredential.roll_number == student['roll']).first()
    if credential and credential.must_change_password:
        return redirect(url_for('change_password'))

    container_id = socket.gethostname()
    now = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")
    return render_template(
        'index.html',
        container_id=container_id,
        timestamp=now,
        student=student
    )

@app.route('/result', methods=['GET'])
@student_required
def get_result():
    _, student = get_logged_in_student()
    if not student:
        return redirect(url_for('login'))
    
    subjects_with_grades = {}
    for sub, marks in student['subjects'].items():
        grade, label = get_grade(marks)
        subjects_with_grades[sub] = {"marks": marks, "grade": grade, "label": label}
    
    summary = get_result_summary(student['subjects'])
    container_id = socket.gethostname()
    now = datetime.datetime.now().strftime("%d %B %Y, %I:%M %p")
    
    return render_template('result.html', 
                           student=student, 
                           subjects=subjects_with_grades,
                           summary=summary,
                           container_id=container_id,
                           timestamp=now)

@app.route('/api/stats')
def stats():
    role = session.get("auth_role", "anonymous")
    if role == "student":
        identity = session.get("student_roll", "anonymous")
    elif role == "admin":
        identity = session.get("admin_username", "anonymous")
    else:
        identity = "anonymous"

    return jsonify({
        "container_id": socket.gethostname(),
        "uptime": "Running",
        "active_requests": random.randint(1, 50),
        "authenticated_user": identity,
        "role": role,
        "timestamp": datetime.datetime.now().isoformat()
    })


with app.app_context():
    initialize_database_with_retry()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
