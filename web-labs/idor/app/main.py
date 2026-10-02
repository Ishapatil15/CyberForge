from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="CyberForge Lab 2 — IDOR")

PROFILES = {
    1001: {"name": "Sarah Connor", "role": "Junior Analyst", "email": "sarah@nexus.corp", "notes": "Onboarding completed."},
    1002: {"name": "James Cole", "role": "Security Intern", "email": "james@nexus.corp", "notes": "Assigned to incident review."},
    1337: {"name": "Dr. CyberForge Admin", "role": "Chief Security Architect", "email": "admin@nexus.corp", "notes": "RESTRICTED EXECUTIVE COMPLIANCE RECORD. Vault Flag: CTF{1d0r_br0k3n_0bj3ct_auth_449}"}
}

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!doctype html>
    <html lang="en">
    <head><meta charset="utf-8"><title>Personnel Directory</title>
    <style>body { font-family: Inter, sans-serif; background: #070B14; color: #F8FAFC; padding: 2rem; } .card { max-width: 600px; margin: 0 auto; background: #111B2E; border: 1px solid #1E293B; border-radius: 8px; padding: 2rem; } a { color: #00D9FF; }</style>
    </head>
    <body>
      <div class="card">
        <h2>Nexus Personnel Directory</h2>
        <p style="color: #94A3B8;">Welcome, Junior Analyst. Select your profile to view personnel records:</p>
        <ul>
          <li><a href="/profile?id=1001">My Profile (ID: 1001)</a></li>
          <li><a href="/profile?id=1002">Teammate Profile (ID: 1002)</a></li>
        </ul>
      </div>
    </body>
    </html>
    """

@app.get("/profile", response_class=HTMLResponse)
def profile(id: int = 1001):
    user = PROFILES.get(id)
    if not user:
        return HTMLResponse("<h3>Profile Not Found</h3><a href='/'>Back</a>", status_code=404)
    name = user['name']
    role = user['role']
    email = user['email']
    notes = user['notes']
    return f"""
    <!doctype html>
    <html lang="en">
    <head><meta charset="utf-8"><title>Personnel Profile</title>
    <style>body {{ font-family: Inter, sans-serif; background: #070B14; color: #F8FAFC; padding: 2rem; }} .card {{ max-width: 600px; margin: 0 auto; background: #111B2E; border: 1px solid #1E293B; border-radius: 8px; padding: 2rem; }} a {{ color: #00D9FF; }}</style>
    </head>
    <body>
      <div class="card">
        <h2>Personnel Record #{id}</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Role:</strong> {role}</p>
        <p><strong>Email:</strong> {email}</p>
        <div style="background: #0D1422; border-left: 4px solid #00D9FF; padding: 1rem; margin-top: 1rem;">
          <strong>Confidential Personnel Notes:</strong><br/>
          {notes}
        </div>
        <p style="margin-top: 1.5rem;"><a href="/">Back to Directory</a></p>
      </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)
