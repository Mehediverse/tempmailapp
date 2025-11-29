from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

PASSWORD = "mypassword"  # CHANGE THIS
INBOX = []

@app.get("/", response_class=HTMLResponse)
def login():
    return """
    <h2>Login</h2>
    <form action="/auth" method="post">
        <input type="password" name="password" placeholder="Password">
        <button>Login</button>
    </form>
    """

@app.post("/auth")
def auth(password: str = Form(...)):
    if password == PASSWORD:
        r = RedirectResponse("/inbox", status_code=302)
        r.set_cookie("auth", PASSWORD)
        return r
    return RedirectResponse("/", status_code=302)

def check_auth(request: Request):
    return request.cookies.get("auth") == PASSWORD

@app.get("/inbox", response_class=HTMLResponse)
def view_inbox(request: Request):
    if not check_auth(request):
        return RedirectResponse("/", status_code=302)
    html = "<h2>Inbox</h2>"
    for mail in INBOX:
        html += f"<p><b>From:</b> {mail['sender']}<br>"
        html += f"<b>Subject:</b> {mail['subject']}<br>"
        html += f"<pre>{mail['body']}</pre><hr></p>"
    return html

@app.post("/email")
def receive(sender: str = Form(...), subject: str = Form(...), body: str = Form(...)):
    INBOX.append({
        "sender": sender,
        "subject": subject,
        "body": body
    })
    return {"status": "stored"}
