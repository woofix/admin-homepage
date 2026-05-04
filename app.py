from flask import Flask, request, Response, redirect
import os

app = Flask(__name__)

CONFIG_DIR = "/homepage-config"
FILES = ["services.yaml", "settings.yaml", "widgets.yaml", "bookmarks.yaml", "docker.yaml"]

USER = os.getenv("ADMIN_USER", "admin")
PASS = os.getenv("ADMIN_PASS", "admin")

def check_auth():
    auth = request.authorization
    return auth and auth.username == USER and auth.password == PASS

def require_auth():
    return Response(
        "Authentification requise",
        401,
        {"WWW-Authenticate": 'Basic realm="Homepage Admin"'}
    )

@app.before_request
def auth():
    if not check_auth():
        return require_auth()

@app.route("/", methods=["GET"])
def index():
    links = "".join([f'<li><a href="/edit/{f}">{f}</a></li>' for f in FILES])
    return f"""
    <html>
    <head>
      <title>Homepage Admin</title>
      <style>
        body {{ font-family: Arial; background:#111; color:#eee; padding:30px; }}
        a {{ color:#7ab7ff; font-size:20px; }}
        li {{ margin:12px 0; }}
      </style>
    </head>
    <body>
      <h1>Homepage Admin</h1>
      <ul>{links}</ul>
    </body>
    </html>
    """

@app.route("/edit/<filename>", methods=["GET", "POST"])
def edit(filename):
    if filename not in FILES:
        return "Fichier interdit", 403

    path = os.path.join(CONFIG_DIR, filename)

    if request.method == "POST":
        content = request.form.get("content", "")
        with open(path, "w") as f:
            f.write(content)
        return redirect(f"/edit/{filename}")

    content = ""
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()

    return f"""
    <html>
    <head>
      <title>{filename}</title>
      <style>
        body {{ font-family: Arial; background:#111; color:#eee; padding:20px; }}
        textarea {{ width:100%; height:80vh; background:#1e1e1e; color:#eee; font-family:monospace; font-size:14px; }}
        button {{ padding:10px 18px; margin-top:10px; font-size:16px; }}
        a {{ color:#7ab7ff; }}
      </style>
    </head>
    <body>
      <a href="/">← Retour</a>
      <h2>{filename}</h2>
      <form method="post">
        <textarea name="content">{content}</textarea>
        <br>
        <button type="submit">Enregistrer</button>
      </form>
    </body>
    </html>
    """

app.run(host="0.0.0.0", port=8099)
