from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI(title="CyberForge Lab 3 — File Upload")
UPLOAD_DIR = Path("/tmp/cyberforge_lab_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!doctype html>
    <html lang="en">
    <head><meta charset="utf-8"><title>Secure Report Upload Portal</title>
    <style>body { font-family: Inter, sans-serif; background: #070B14; color: #F8FAFC; padding: 2rem; } .card { max-width: 600px; margin: 0 auto; background: #111B2E; border: 1px solid #1E293B; border-radius: 8px; padding: 2rem; } input { margin: 1rem 0; } button { background: #00D9FF; color: #070B14; font-weight: bold; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; cursor: pointer; } a { color: #00D9FF; }</style>
    </head>
    <body>
      <div class="card">
        <h2>Document Verification & Upload Portal</h2>
        <p style="color: #94A3B8;">Submit an audit report file (.txt, .log) for automated processing.</p>
        <form action="/upload" method="post" enctype="multipart/form-data">
          <input type="file" name="file" required /><br/>
          <button type="submit">Upload Document</button>
        </form>
      </div>
    </body>
    </html>
    """

@app.post("/upload", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    filename = file.filename or "unknown"
    contents = await file.read()
    dest = UPLOAD_DIR / filename
    dest.write_bytes(contents)

    msg = f"File '{filename}' uploaded successfully. Parser status: Processed {len(contents)} bytes."
    flag_box = ""
    if "override" in filename.lower() or "flag" in filename.lower() or b"override" in contents.lower():
        flag_box = "<div style='background: #0D1422; border-left: 4px solid #22C55E; padding: 1rem; margin: 1rem 0;'><strong>Security Diagnostic Override Triggered:</strong><br/>Flag: CTF{f1l3_upl0ad_byp4ss_succ3ss_321}</div>"

    return f"""
    <!doctype html>
    <html lang="en">
    <head><meta charset="utf-8"><title>Upload Status</title>
    <style>body {{ font-family: Inter, sans-serif; background: #070B14; color: #F8FAFC; padding: 2rem; }} .card {{ max-width: 600px; margin: 0 auto; background: #111B2E; border: 1px solid #1E293B; border-radius: 8px; padding: 2rem; }} a {{ color: #00D9FF; }}</style>
    </head>
    <body>
      <div class="card">
        <h2>Upload Processed</h2>
        <p>{msg}</p>
        {flag_box}
        <a href="/">Back to upload</a>
      </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8013)
