from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "my_secret_key"
def get_db_connection():

    connection = sqlite3.connect("database.db")

    connection.row_factory = sqlite3.Row

    return connection


def create_table():

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.commit()

    connection.close()


@app.route("/")
def home():
    return render_template("home.html")

# register route
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()

        try:

            connection.execute(
                """
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
                """,
                (name, email, hashed_password)
            )

            connection.commit()

        except sqlite3.IntegrityError:

            connection.close()

            return render_template("register.html", error="Email already registered")

        connection.close()

        return "Registration Successful"

    return render_template("register.html")

# login route
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()

        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        connection.close()

        # if user is None:

        #     return "Invalid Email or Password"

        # if not check_password_hash(user["password"], password):

        #     return "Invalid Email or Password"
        if user is None:
            return render_template("login.html", error="Invalid Email or Password")
        if not check_password_hash(user["password"], password):
            return render_template("login.html", error="Invalid Email or Password")
       

        session["user_name"] = user["name"]
        

        return redirect(url_for("dashboard"))
    return render_template("login.html")


# dashboard route
@app.route("/dashboard")
def dashboard():

    if "user_name" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")


# logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":

    create_table()
    app.run(debug=True)