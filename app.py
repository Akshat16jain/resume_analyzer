from flask import Flask, render_template, request, redirect, session
from db import Base, engine, SessionLocal
import model
import analyzer
import PyPDF2
import docx
import json


app = Flask(__name__)
app.secret_key = "secret123"


# Create database tables
Base.metadata.create_all(bind=engine)


# ---------------- HOME ----------------

@app.route("/")
def Home():

    if "user" in session:
        return redirect("/Dashboard")

    return redirect("/login")


# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    db = SessionLocal()

    try:

        if request.method == "POST":

            email = request.form.get("email")
            password = request.form.get("password")

            # Check existing user
            existing_user = db.query(model.User).filter_by(
                email=email
            ).first()

            if existing_user:
                return "User already exists"

            # Create new user
            user = model.User(
                email=email,
                password=password
            )

            db.add(user)
            db.commit()

            return redirect("/login")

        return render_template("signup.html")

    finally:
        db.close()


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    db = SessionLocal()

    try:

        if request.method == "POST":

            email = request.form.get("email")
            password = request.form.get("password")

            # Find user
            user = db.query(model.User).filter_by(
                email=email
            ).first()

            # Check email and password
            if user and user.password == password:

                session["user"] = user.email

                return redirect("/Dashboard")

            else:

                return "Invalid email or password"

        return render_template("login.html")

    finally:
        db.close()


# ---------------- DASHBOARD ----------------

@app.route("/Dashboard", methods=["GET", "POST"])
def Dashboard():

    # Check login
    if "user" not in session:
        return redirect("/login")

    result = None

    resume_text = ""
    user_goal = ""

    if request.method == "POST":

        # Get role from form
        user_goal = request.form.get("role", "")

        # Get resume text from textarea
        resume_text = request.form.get("resume", "")

        # Get uploaded file
        file = request.files.get("file")

        # ---------------- PDF ----------------

        if file and file.filename:

            if file.filename.lower().endswith(".pdf"):

                reader = PyPDF2.PdfReader(file)

                resume_text = ""

                for page in reader.pages:
                    resume_text += page.extract_text() or ""

            # ---------------- DOCX ----------------

            elif file.filename.lower().endswith(".docx"):

                document = docx.Document(file)

                resume_text = "\n".join(
                    paragraph.text
                    for paragraph in document.paragraphs
                )

        # ---------------- ANALYZE RESUME ----------------

        if resume_text and user_goal:

            # IMPORTANT:
            # analyze_resume() is inside analyzer.py
            result = analyzer.analyze_resume(
                resume_text,
                user_goal
            )

            # ---------------- SAVE REPORT ----------------

            db = SessionLocal()

            try:

                user = db.query(model.User).filter_by(
                    email=session["user"]
                ).first()

                if user:

                    report = model.Reports(
                        user_id=user.id,
                        resume_text=resume_text,
                        result=json.dumps(result)
                    )

                    db.add(report)
                    db.commit()

            finally:
                db.close()

    return render_template(
        "Dashboard.html",
        user=session["user"],
        result=result
    )


# ---------------- HISTORY ----------------

@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()

    try:

        # Get logged-in user
        user = db.query(model.User).filter_by(
            email=session["user"]
        ).first()

        if not user:
            return redirect("/login")

        # Get user's reports
        reports = db.query(model.Reports).filter_by(
            user_id=user.id
        ).all()

        # Convert JSON string to dictionary
        parsed_reports = []

        for r in reports:

            try:

                parsed_result = json.loads(r.result)

            except Exception:

                parsed_result = {}

            parsed_reports.append({
                "resume": r.resume_text,
                "result": parsed_result
            })

        return render_template(
            "history.html",
            reports=parsed_reports
        )

    finally:
        db.close()


# ---------------- LOGOUT ----------------

@app.route("/Logout")
def Logout():

    session.pop("user", None)

    return redirect("/login")


# ---------------- RUN APP ----------------

if __name__ == "__main__":

    app.run(debug=True)