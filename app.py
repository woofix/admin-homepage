from flask import Flask, request, redirect, session
import os
import html

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")

CONFIG_DIR = "/homepage-config"

FILES = {
    "Services": "services.yaml",
    "Settings": "settings.yaml",
    "Widgets": "widgets.yaml",
    "Bookmarks": "bookmarks.yaml",
    "Docker": "docker.yaml",
}

USER = os.getenv("ADMIN_USER", "admin")
PASS = os.getenv("ADMIN_PASS", "admin")

def is_logged():
    return session.get("logged") is True

def require_login():
    if not is_logged():
        return redirect("/login")

@app.before_request
def auth():
    if request.path == "/login":
        return
    if not is_logged():
        return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == USER and password == PASS:
            session["logged"] = True
            return redirect("/")
        error = "<p style='color:#ff7777;'>Invalid username or password</p>"

    return f"""
    <html>
    <head>
      <title>Homepage Admin - Login</title>
      <style>
        body {{
          font-family: Arial;
          background:#111;
          color:#eee;
          display:flex;
          align-items:center;
          justify-content:center;
          height:100vh;
          margin:0;
        }}
        .box {{
          background:#181818;
          padding:30px;
          border:1px solid #333;
          border-radius:10px;
          width:320px;
        }}
        input {{
          width:100%;
          padding:10px;
          margin:8px 0;
          background:#1e1e1e;
          color:#eee;
          border:1px solid #444;
          border-radius:6px;
        }}
        button {{
          width:100%;
          padding:10px;
          margin-top:10px;
          font-size:16px;
          cursor:pointer;
          background:#2d7dff;
          color:white;
          border:0;
          border-radius:6px;
          font-weight:bold;
        }}
      </style>
    </head>
    <body>
      <form class="box" method="post">
        <h2>Homepage Admin</h2>
        {error}
        <input name="username" placeholder="Username" autofocus>
        <input name="password" type="password" placeholder="Password">
        <button type="submit">Login</button>
      </form>
    </body>
    </html>
    """

def layout(content):
    buttons = "".join([
        f'<a class="btn" href="/edit/{key}">{key}</a>' for key in FILES
    ])
    logout = '<a class="btn logout" href="/logout">Logout</a>'

    return f"""
    <html>
    <head>
      <title>Homepage Admin</title>
      <style>
        body {{ font-family: Arial; background:#111; color:#eee; margin:0; }}
        header {{ position: sticky; top: 0; background:#181818; padding:15px 20px; border-bottom:1px solid #333; z-index:10; }}
        h1 {{ margin:0 0 12px 0; }}
        .btn {{ display:inline-block; background:#2d7dff; color:white; text-decoration:none; padding:10px 14px; border-radius:6px; margin:4px; font-weight:bold; }}
        .btn:hover {{ background:#5595ff; }}
        .logout {{ background:#aa3333; }}
        .logout:hover {{ background:#cc4444; }}
        main {{ padding:20px; }}
        textarea {{ width:100%; height:75vh; background:#1e1e1e; color:#eee; font-family:monospace; font-size:14px; border:1px solid #444; border-radius:6px; padding:10px; }}
        button {{ padding:10px 18px; margin-top:10px; font-size:16px; cursor:pointer; }}
      </style>
    </head>
    <body>
      <header>
        <h1>Homepage Admin</h1>
        <nav>{buttons}{logout}</nav>
      </header>
      <main>{content}</main>
    </body>
    </html>
    """

@app.route("/", methods=["GET"])
def index():
    return layout("<p>Select a file to edit.</p>")

@app.route("/edit/<key>", methods=["GET", "POST"])
def edit(key):
    if key not in FILES:
        return "Banned file", 403

    filename = FILES[key]
    path = os.path.join(CONFIG_DIR, filename)

    if request.method == "POST":
        content = request.form.get("content", "")
        with open(path, "w") as f:
            f.write(content)
        return redirect(f"/edit/{key}")

    content = ""
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()

    return layout(f"""
      <h2>{key}</h2>
      <form method="post">
        <textarea name="content">{html.escape(content)}</textarea>
        <br>
        <button type="submit">Save</button>
      </form>
    """)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7099)
