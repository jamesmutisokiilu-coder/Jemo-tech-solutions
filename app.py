from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# ==========================================
# CONFIG
# ==========================================
app.secret_key = os.environ.get("SECRET_KEY", "jemo_secret_key")

DATABASE_URL = os.environ.get("DATABASE_URL")

# Fix Render postgres URL format
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ==========================================
# MODELS
# ==========================================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Support(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(100))
    category = db.Column(db.String(100))
    priority = db.Column(db.String(100))
    message = db.Column(db.Text)


class Training(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    course = db.Column(db.String(200))
    email = db.Column(db.String(200))


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    service = db.Column(db.String(200))
    date = db.Column(db.String(100))


# Create tables
with app.app_context():
    db.create_all()

# ==========================================
# HOME
# ==========================================
@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# REGISTER
# ==========================================
@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""

    if request.method == "POST":
        try:
            user = User(
                username=request.form["username"],
                email=request.form["email"],
                password=request.form["password"]
            )

            db.session.add(user)
            db.session.commit()

            return redirect(url_for("login"))

        except Exception as e:
            message = f"Error: {str(e)}"

    return render_template("register.html", message=message)


# ==========================================
# LOGIN
# ==========================================
@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        user = User.query.filter_by(
            email=request.form["email"],
            password=request.form["password"]
        ).first()

        if user:
            session["user"] = user.username
            return redirect(url_for("dashboard"))
        else:
            message = "Invalid login details"

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
        s = Support(
            name=request.form["name"],
            email=request.form["email"],
            phone=request.form["phone"],
            category=request.form["category"],
            priority=request.form["priority"],
            message=request.form["message"]
        )

        db.session.add(s)
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
        t = Training(
            name=request.form["name"],
            course=request.form["course"],
            email=request.form["email"]
        )

        db.session.add(t)
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
        b = Booking(
            name=request.form["name"],
            service=request.form["service"],
            date=request.form["date"]
        )

        db.session.add(b)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("booking.html")


# ==========================================
# RUN APP
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
