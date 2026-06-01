from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# ==========================================
# APP CONFIG
# ==========================================
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "jemo_secret_key")

# ==========================================
# DATABASE CONFIG (NO psycopg2)
# ==========================================
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not set in environment variables")

# FIX POSTGRES DRIVER FOR pg8000
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+pg8000://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==========================================
# MODELS (FIXED + SAFE TABLE NAME)
# ==========================================
class User(db.Model):
    __tablename__ = "users"   # 🔥 IMPORTANT FIX (prevents your error)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)


class Support(db.Model):
    __tablename__ = "support"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(50))
    category = db.Column(db.String(100))
    priority = db.Column(db.String(50))
    message = db.Column(db.Text)


class TrainingRequest(db.Model):
    __tablename__ = "training_requests"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    course = db.Column(db.String(150))
    email = db.Column(db.String(150))


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    service = db.Column(db.String(150))
    date = db.Column(db.String(50))


# ==========================================
# SAFE TABLE CREATION
# ==========================================
with app.app_context():
    db.create_all()

# ==========================================
# HOME
# ==========================================
@app.route("/")
def home():
    return render_template("index.html")

# ==========================================
# REGISTER (FIXED + SAFE)
# ==========================================
@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            existing = User.query.filter_by(email=email).first()

            if existing:
                return render_template("register.html", message="Email already exists")

            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password)
            )

            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for("login"))

        except Exception as e:
            db.session.rollback()
            return render_template("register.html", message=f"Database error: {str(e)}")

    return render_template("register.html", message=message)

# ==========================================
# LOGIN
# ==========================================
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            user = User.query.filter_by(email=email).first()

            if user and check_password_hash(user.password, password):
                session["user"] = user.username
                return redirect(url_for("dashboard"))
            else:
                message = "Invalid login details"

        except Exception as e:
            message = f"Database error: {str(e)}"

    return render_template("login.html", message=message)

# ==========================================
# DASHBOARD
# ==========================================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", username=session["user"])

# ==========================================
# LOGOUT
# ==========================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ==========================================
# PROTECTED PAGES
# ==========================================
def protected(page):
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template(page)

@app.route("/services")
def services():
    return protected("services.html")

@app.route("/portfolio")
def portfolio():
    return protected("portfolio.html")

@app.route("/blog")
def blog():
    return protected("blog.html")

@app.route("/downloads")
def downloads():
    return protected("downloads.html")

@app.route("/about")
def about():
    return protected("about.html")

@app.route("/contact")
def contact():
    return protected("contact.html")

# ==========================================
# SUPPORT
# ==========================================
@app.route("/support", methods=["GET", "POST"])
def support():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        new_support = Support(
            name=request.form["name"],
            email=request.form["email"],
            phone=request.form["phone"],
            category=request.form["category"],
            priority=request.form["priority"],
            message=request.form["message"]
        )

        db.session.add(new_support)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("support.html")

# ==========================================
# TRAINING
# ==========================================
@app.route("/training", methods=["GET", "POST"])
def training():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        req = TrainingRequest(
            name=request.form["name"],
            course=request.form["course"],
            email=request.form["email"]
        )

        db.session.add(req)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("training.html")

# ==========================================
# BOOKING
# ==========================================
@app.route("/booking", methods=["GET", "POST"])
def booking():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        book = Booking(
            name=request.form["name"],
            service=request.form["service"],
            date=request.form["date"]
        )

        db.session.add(book)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("booking.html")

# ==========================================
# RUN
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
