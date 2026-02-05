from flask import Flask, request, redirect
import sqlite3
import random
import string

app = Flask(__name__)

# ---------- Database ----------
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
            long TEXT
        )
    """)
    conn.commit()
    conn.close()

# ---------- Short URL Generator ----------
def generate_short_url():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(6))

# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        long_url = request.form["long_url"]
        short_url = generate_short_url()

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO urls (short, long) VALUES (?, ?)",
            (short_url, long_url)
        )
        conn.commit()
        conn.close()

        return f"""
        <h3>Short URL created!</h3>
        <a href='/{short_url}'>http://127.0.0.1:5000/{short_url}</a>
        """

    return """
        <h2>URL Shortener (Flask)</h2>
        <form method="post">
            <input type="url" name="long_url" required>
            <button type="submit">Shorten</button>
        </form>
    """

@app.route("/<short>")
def redirect_to_long(short):
    conn = get_db_connection()
    url = conn.execute(
        "SELECT long FROM urls WHERE short = ?",
        (short,)
    ).fetchone()
    conn.close()

    if url:
        return redirect(url["long"])
    return "URL not found", 404

# ---------- Run ----------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
