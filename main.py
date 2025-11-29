from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from datetime import datetime
from typing import List, Dict, Optional

app = FastAPI()

# ========= CONFIG =========
PASSWORD = "Mr$Z@MPdNKY][Ymw6Ee@"  # 🔒 CHANGE THIS
APP_TITLE = "CorePay TempMail"
DOMAIN = "corepaytg.online"
POLL_INTERVAL_MS = 3000  # auto-refresh every 3 seconds
# ==========================

INBOX: List[Dict] = []   # in-memory messages


# ---------- Helpers ----------

def is_authed(request: Request) -> bool:
    return request.cookies.get("auth") == PASSWORD


def html_page(body: str, title: Optional[str] = None) -> HTMLResponse:
    if title is None:
        title = APP_TITLE
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>{title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
            :root {{
                --bg: #050816;
                --card: #0f172a;
                --accent: #38bdf8;
                --accent-soft: rgba(56,189,248,0.1);
                --text: #e5e7eb;
                --muted: #9ca3af;
                --danger: #f97373;
            }}
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                min-height: 100vh;
                font-family: system-ui, -apple-system, BlinkMacSystemFont,
                             "Segoe UI", sans-serif;
                background: radial-gradient(circle at top, #0f172a 0,
                          #020617 45%, #000000 100%);
                color: var(--text);
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }}
            .card {{
                width: 100%;
                max-width: 980px;
                background: linear-gradient(135deg, #020617, #020617) padding-box,
                           linear-gradient(135deg, rgba(56,189,248,0.3),
                           rgba(129,140,248,0.4)) border-box;
                border: 1px solid rgba(148,163,184,0.25);
                border-radius: 18px;
                padding: 22px 24px 20px;
                box-shadow: 0 24px 90px rgba(15,23,42,0.9);
                backdrop-filter: blur(18px);
            }}
            .card-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 18px;
                gap: 8px;
            }}
            .title {{
                font-size: 1.25rem;
                font-weight: 600;
                letter-spacing: 0.02em;
            }}
            .subtitle {{
                font-size: 0.8rem;
                color: var(--muted);
            }}
            .badge {{
                padding: 4px 10px;
                border-radius: 999px;
                font-size: 0.7rem;
                border: 1px solid var(--accent-soft);
                background: rgba(15,23,42, 0.85);
                color: var(--accent);
            }}
            .field-label {{
                font-size: 0.8rem;
                color: var(--muted);
                margin-bottom: 4px;
            }}
            input[type="password"],
            input[type="text"] {{
                width: 100%;
                padding: 10px 11px;
                border-radius: 999px;
                border: 1px solid rgba(148,163,184,0.3);
                background: rgba(15,23,42,0.9);
                color: var(--text);
                font-size: 0.9rem;
                outline: none;
                transition: border-color 0.15s, box-shadow 0.15s, background 0.15s;
            }}
            input:focus {{
                border-color: var(--accent);
                box-shadow: 0 0 0 1px rgba(56,189,248,0.3);
                background: rgba(15,23,42,1);
            }}
            button {{
                border: none;
                border-radius: 999px;
                padding: 9px 18px;
                font-size: 0.9rem;
                font-weight: 500;
                cursor: pointer;
                background: linear-gradient(135deg, #38bdf8, #6366f1);
                color: white;
                box-shadow: 0 12px 30px rgba(37,99,235,0.45);
                display: inline-flex;
                align-items: center;
                gap: 6px;
                transition: transform 0.1s, box-shadow 0.1s, filter 0.1s;
            }}
            button:hover {{
                transform: translateY(-1px);
                filter: brightness(1.05);
                box-shadow: 0 16px 40px rgba(37,99,235,0.6);
            }}
            button.secondary {{
                background: transparent;
                border: 1px solid rgba(148,163,184,0.35);
                box-shadow: none;
                color: var(--muted);
            }}
            button.secondary:hover {{
                border-color: rgba(148,163,184,0.7);
                filter: none;
                transform: none;
            }}
            .login-layout {{
                display: grid;
                grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
                gap: 18px;
            }}
            @media (max-width: 768px) {{
                .card {{
                    padding: 18px 16px 16px;
                }}
                .login-layout {{
                    grid-template-columns: minmax(0, 1fr);
                }}
                .card-header {{
                    flex-direction: column;
                    align-items: flex-start;
                }}
            }}
            .pill {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 4px 10px;
                border-radius: 999px;
                background: rgba(15,23,42,0.9);
                border: 1px solid rgba(148,163,184,0.35);
                font-size: 0.75rem;
                color: var(--muted);
            }}
            .pill span {{
                color: var(--accent);
                font-weight: 500;
            }}
            .hint {{
                font-size: 0.75rem;
                color: var(--muted);
                margin-top: 6px;
            }}
            .error {{
                color: var(--danger);
                font-size: 0.8rem;
                margin-bottom: 6px;
            }}
            .table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            .table th, .table td {{
                padding: 8px 6px;
                font-size: 0.8rem;
                text-align: left;
            }}
            .table th {{
                font-weight: 500;
                color: var(--muted);
                border-bottom: 1px solid rgba(148,163,184,0.3);
            }}
            .table tr:nth-child(even) {{
                background: rgba(15,23,42,0.5);
            }}
            .table tr:hover {{
                background: rgba(15,23,42,0.85);
            }}
            .mono {{
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
                             "Liberation Mono", "Courier New", monospace;
            }}
            .subject {{
                font-weight: 500;
                color: #e5e7eb;
            }}
            .body-preview {{
                color: var(--muted);
                max-width: 420px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .empty {{
                padding: 22px 10px 8px;
                text-align: center;
                color: var(--muted);
                font-size: 0.9rem;
            }}
            a {{ color: var(--accent); text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="card">
            {body}
        </div>
    </body>
    </html>
    """
    return HTMLResponse(full_html)


# ---------- UI Routes ----------

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    if is_authed(request):
        return RedirectResponse("/inbox", status_code=302)

    error_html = f'<div class="error">{error}</div>' if error else ""
    body = f"""
    <div class="card-header">
        <div>
            <div class="title">{APP_TITLE}</div>
            <div class="subtitle">Secure access to your private temp inbox</div>
        </div>
        <div class="badge mono">🔒 Owner Access Only</div>
    </div>

    <div class="login-layout">
        <div>
            <div class="field-label">Password</div>
            {error_html}
            <form method="post" action="/auth">
                <input type="password" name="password" placeholder="Enter your access password" autofocus />
                <div style="margin-top: 14px; display:flex; gap:10px; align-items:center;">
                    <button type="submit">Unlock inbox</button>
                    <div class="hint">Change it in <span class="mono">PASSWORD</span> inside <span class="mono">main.py</span>.</div>
                </div>
            </form>
        </div>
        <div>
            <div class="pill">
                <span>@{DOMAIN}</span> · single-user panel
            </div>
            <div class="hint" style="margin-top:10px;">
                Public URL, private inbox. Only users with the password can read messages.
            </div>
            <div class="hint" style="margin-top:10px;">
                This app stores messages <b>only in memory</b>. Redeploying the service will clear the inbox.
            </div>
        </div>
    </div>
    """
    return html_page(body, title="Login · " + APP_TITLE)


@app.post("/auth")
async def auth(password: str = Form(...)):
    if password == PASSWORD:
        resp = RedirectResponse("/inbox", status_code=302)
        resp.set_cookie("auth", PASSWORD, httponly=True, secure=True)
        return resp
    return RedirectResponse("/?error=Wrong+password", status_code=302)


@app.get("/logout")
async def logout():
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("auth")
    return resp


@app.get("/inbox", response_class=HTMLResponse)
async def inbox_page(request: Request):
    if not is_authed(request):
        return RedirectResponse("/", status_code=302)

    body = f"""
    <div class="card-header">
        <div>
            <div class="title">Inbox</div>
            <div class="subtitle mono">{DOMAIN} · <span id="msg-count">0</span> messages</div>
        </div>
        <div style="display:flex; gap:8px; align-items:center;">
            <span class="hint mono">Auto-refresh: {POLL_INTERVAL_MS/1000:.1f}s</span>
            <a href="/logout"><button class="secondary">Log out</button></a>
        </div>
    </div>

    <div id="inbox-container">
        <div class="empty">Loading messages…</div>
    </div>

    <script>
    const intervalMs = {POLL_INTERVAL_MS};

    async function loadInbox() {{
        try {{
            const res = await fetch('/api/inbox');
            if (res.status === 401 || res.status === 403) {{
                window.location.href = '/';
                return;
            }}
            const data = await res.json();
            const msgs = data.messages || [];
            const container = document.getElementById('inbox-container');
            const countEl = document.getElementById('msg-count');
            if (countEl) countEl.textContent = msgs.length;

            if (msgs.length === 0) {{
                container.innerHTML = '<div class="empty">No messages yet. When your backend posts to <span class="mono">/email</span>, they will appear here automatically.</div>';
                return;
            }}

            let rows = '';
            for (let i = msgs.length - 1; i >= 0; i--) {{
                const m = msgs[i];
                const idx = i;
                const preview = (m.body || '').replace(/\\n/g, ' ');
                const shortPreview = preview.length > 120 ? preview.slice(0,120) + '…' : preview;
                rows += `
                <tr>
                    <td class="mono" style="font-size:0.75rem;">${{idx}}</td>
                    <td class="mono" style="font-size:0.75rem;">${{m.time}}</td>
                    <td class="mono" style="font-size:0.8rem;">${{m.sender}}</td>
                    <td class="subject">${{m.subject || '(no subject)'}}</td>
                    <td class="body-preview mono">${{shortPreview}}</td>
                </tr>`;
            }}

            container.innerHTML = `
                <table class="table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Received (UTC)</th>
                            <th>From</th>
                            <th>Subject</th>
                            <th>Body (preview)</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            `;
        }} catch (e) {{
            console.error('Failed to load inbox', e);
        }}
    }}

    loadInbox();                          // first load
    setInterval(loadInbox, intervalMs);   // auto refresh
    </script>
    """
    return html_page(body, title="Inbox · " + APP_TITLE)


# ---------- JSON API (used by JS auto-refresh) ----------

@app.get("/api/inbox")
async def api_inbox(request: Request):
    if not is_authed(request):
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    return JSONResponse({"messages": INBOX})


# ---------- "Email" receive endpoint ----------

@app.post("/email")
async def receive_email(
    sender: str = Form(...),
    subject: str = Form(""),
    body: str = Form(""),
):
    INBOX.append(
        {
            "sender": sender,
            "subject": subject,
            "body": body,
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    return JSONResponse({"status": "ok", "stored": True, "index": len(INBOX) - 1})
