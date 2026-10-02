from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import sqlite3

app = FastAPI(title="CyberForge Lab 1 — SQL Injection")

# In-memory database initialization
conn = sqlite3.connect(":memory:", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
cur.execute("CREATE TABLE admin_secrets (id INTEGER PRIMARY KEY, secret_name TEXT, flag TEXT)")
cur.execute("INSERT INTO users VALUES (1, 'alice', 'alice_pass_123', 'student')")
cur.execute("INSERT INTO users VALUES (2, 'bob', 'bob_pass_456', 'student')")
cur.execute("INSERT INTO admin_secrets VALUES (1, 'production_vault_flag', 'CTF{sqli_un10n_inj3ct10n_pwnd_817}')")
conn.commit()

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>CyberForge Lab // Student Portal</title>
      <style>
        body { font-family: Inter, sans-serif; background: #070B14; color: #F8FAFC; padding: 2rem; }
        .card { max-width: 600px; margin: 0 auto; background: #111B2E; border: 1px solid #1E293B; border-radius: 8px; padding: 2rem; }
        input { width: 100%; padding: 0.75rem; background: #0D1422; border: 1px solid #1E293B; color: #fff; margin-bottom: 1rem; border-radius: 4px; box-sizing: border-box; }
        button { background: #00D9FF; color: #070B14; font-weight: bold; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; cursor: pointer; }
        .result { margin-top: 1rem; padding: 1rem; background: #0D1422; border: 1px solid #1E293B; border-radius: 4px; }
      </style>
    </head>
    <body>
      <div class="card">
        <h2>CyberForge Student Directory Search</h2>
        <p style="color: #94A3B8;">Search for student records or test your database query interface.</p>
        <form action="/search" method="get">
          <input type="text" name="q" placeholder="Enter student username (e.g. alice)" required />
          <button type="submit">Search Database</button>
        </form>
      </div>
    </body>
    </html>
    """

@app.get("/search", response_class=HTMLResponse)
def search(q: str):
    query = "SELECT id, username, role FROM users WHERE username = '" + q + "'"
    try:
        cur.execute(query)
        rows = cur.fetchall()
        html_rows = "".join([f"<li>ID: {r[0]} | User: {r[1]} | Role: {r[2]}</li>" for r in rows])
        results = f"<ul>{html_rows}</ul>" if rows else "<p>No matching records found.</p>"
    except Exception as e:
        results = f"<p style='color: #EF4444;'>SQL Error: {e}</p>"

    return f"""
    <!doctype html>
    <html lang="en">
    <head><meta charset="utf-8"><title>Search Results</title>
    <style>body {{ font-family: Inter, sans-serif; background: #070B14; color: #F8FAFC; padding: 2rem; }} .card {{ max-width: 600px; margin: 0 auto; background: #111B2E; border: 1px solid #1E293B; padding: 2rem; border-radius: 8px; }} a {{ color: #00D9FF; }}</style>
    </head>
    <body>
      <div class="card">
        <h2>Query Results</h2>
        <p>Executed: <code>{query}</code></p>
        <div style="background: #0D1422; padding: 1rem; border-radius: 4px; margin: 1rem 0;">{results}</div>
        <a href="/">Back to search</a>
      </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
