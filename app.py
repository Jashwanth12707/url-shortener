from flask import Flask, request, redirect, render_template
import sqlite3
import random
import string

app = Flask(__name__)

# ---------------- DATABASE ----------------

def get_db_connection():
    conn = sqlite3.connect("urls.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short TEXT UNIQUE,
            long TEXT UNIQUE,
            clicks INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


# ---------------- SHORT URL GENERATOR ----------------

def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))


# ---------------- ROUTES ----------------

@app.route("/", methods=["GET", "POST"])
def home():
    short_url = None
    clicks = None

    if request.method == "POST":
        long_url = request.form["long_url"]
        conn = get_db_connection()

        # check if URL already exists
        existing = conn.execute(
            "SELECT short, clicks FROM urls WHERE long = ?",
            (long_url,)
        ).fetchone()

        if existing:
            short_url = existing["short"]
            clicks = existing["clicks"]
        else:
            short_url = generate_short_url()
            conn.execute(
                "INSERT INTO urls (short, long) VALUES (?, ?)",
                (short_url, long_url)
            )
            conn.commit()
            clicks = 0

        conn.close()

    return render_template(
        "index.html",
        short_url=short_url,
        clicks=clicks
    )


@app.route("/<short>")
def redirect_to_long(short):
    conn = get_db_connection()

    url = conn.execute(
        "SELECT long, clicks FROM urls WHERE short = ?",
        (short,)
    ).fetchone()

    if url:
       
        conn.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE short = ?",
            (short,)
        )
        conn.commit()
        conn.close()
        return redirect(url["long"])

    conn.close()
    return "URL not found", 404


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
