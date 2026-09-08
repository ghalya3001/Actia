import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import uvicorn
from sqlalchemy import text
from app.db.session import engine

app = FastAPI(title="ActiaDB Explorer")

CSS = """
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
    body { background: #0f172a; color: #f8fafc; display: flex; height: 100vh; overflow: hidden; }
    .sidebar { width: 260px; background: #1e293b; border-right: 1px solid #334155; padding: 24px 16px; display: flex; flex-direction: column; gap: 20px; }
    .logo { font-size: 1.25rem; font-weight: 700; color: #38bdf8; display: flex; align-items: center; gap: 10px; }
    .table-list { display: flex; flex-direction: column; gap: 8px; }
    .table-item { padding: 10px 14px; border-radius: 8px; color: #94a3b8; text-decoration: none; font-weight: 500; transition: all 0.2s; display: flex; align-items: center; justify-content: space-between; }
    .table-item:hover, .table-item.active { background: #0284c7; color: #ffffff; }
    .main { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: #0f172a; }
    .header { padding: 20px 32px; background: #1e293b; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center; }
    .header h1 { font-size: 1.3rem; font-weight: 600; color: #f8fafc; }
    .content { flex: 1; padding: 32px; overflow: auto; }
    .table-container { background: #1e293b; border-radius: 12px; border: 1px solid #334155; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3); }
    table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85rem; }
    th { background: #0f172a; padding: 14px 18px; color: #38bdf8; font-weight: 600; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em; border-bottom: 1px solid #334155; }
    td { padding: 14px 18px; color: #cbd5e1; border-bottom: 1px solid #334155; max-width: 350px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    tr:hover td { background: rgba(56, 189, 248, 0.05); }
"""

@app.get("/", response_class=HTMLResponse)
def index(table: str = Query("users")):
    allowed_tables = ["users", "hse_audits", "password_reset_tokens", "refresh_tokens", "token_blacklist"]
    if table not in allowed_tables:
        table = "users"

    with engine.connect() as conn:
        result = conn.execute(text(f'SELECT * FROM {table} LIMIT 100'))
        columns = list(result.keys())
        rows = result.fetchall()

    if not columns:
        table_html = "<div style='padding: 20px; color: #94a3b8;'>Aucune donnée dans cette table.</div>"
    else:
        header_th = "".join([f"<th>{col}</th>" for col in columns])
        body_trs = ""
        for row in rows:
            tds = "".join([f"<td>{str(val) if val is not None else '<i style=\"color:#64748b\">null</i>'}</td>" for val in row])
            body_trs += f"<tr>{tds}</tr>"
        table_html = f"<table><thead><tr>{header_th}</tr></thead><tbody>{body_trs}</tbody></table>"

    def is_act(t):
        return "active" if table == t else ""

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>ActiaDB — Explorateur PostgreSQL</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>{CSS}</style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">🗄️ ActiaDB Explorer</div>
        <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Tables PostgreSQL</div>
        <div class="table-list">
            <a href="/?table=users" class="table-item {is_act('users')}"><span>👤 users</span></a>
            <a href="/?table=hse_audits" class="table-item {is_act('hse_audits')}"><span>📝 hse_audits</span></a>
            <a href="/?table=password_reset_tokens" class="table-item {is_act('password_reset_tokens')}"><span>🔑 reset_tokens</span></a>
            <a href="/?table=refresh_tokens" class="table-item {is_act('refresh_tokens')}"><span>🔄 refresh_tokens</span></a>
            <a href="/?table=token_blacklist" class="table-item {is_act('token_blacklist')}"><span>🚫 token_blacklist</span></a>
        </div>
    </div>
    <div class="main">
        <div class="header">
            <h1>Table : <span style="color: #38bdf8;">{table}</span></h1>
            <span style="color: #94a3b8; font-size: 0.85rem;">PostgreSQL 17 | Base: actia_db</span>
        </div>
        <div class="content">
            <div class="table-container">
                {table_html}
            </div>
        </div>
    </div>
</body>
</html>"""

    return HTMLResponse(content=html)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5050)
