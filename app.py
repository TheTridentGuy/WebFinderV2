import re
import secrets
import hashlib
from flask import Flask, request, render_template, send_file
import json
from pathlib import Path

app = Flask(__name__)
CONFIG_PATH = "config.json"


class File:
    def __init__(self, path, name):
        self.is_dir = False
        self.path = path
        self.name = name


class Directory:
    def __init__(self, name, subdirs=(), files=()):
        self.is_dir = True
        self.name = name
        self.subdirs = subdirs
        self.files = files

def generate_dir(path: Path):
    files = []
    subdirs = []
    for file in path.iterdir():
        if file.is_dir():
            subdirs.append(generate_dir(file))
        else:
            files.append(File(path=(path/file).relative_to(FILE_SERVE_PATH), name=file.name))
    return Directory(name=path.name, subdirs=subdirs, files=files)

@app.route("/files")
def files():
    files = generate_dir(Path(FILE_SERVE_PATH))
    return render_template("files.html", files=files, preview=True)


@app.route("/files/<path:filename>")
def file_path(filename):
    path = Path(FILE_SERVE_PATH)/Path(filename)
    return send_file(path, as_attachment=False)


@app.route("/files/upload", methods=["POST", "GET"])
def upload():
    if request.method == "POST":
        password = request.values.get("password")
        if password and hashlib.sha256(password.encode("utf-8")).hexdigest() == UPLOAD_PASS_HASH:
            files = request.files.getlist("files")
            for file in files:
                while (Path(FILE_SERVE_PATH)/Path(file.filename)).exists():
                    file.filename=re.sub(r"(?=\.\w+$)|$", "-"+secrets.token_hex(4), file.filename, count=1)
                print(Path(FILE_SERVE_PATH)/Path(file.filename))
                file.save(Path(FILE_SERVE_PATH)/Path(file.filename))
        else:
            return 401, "Unauthorized"
    else:
        return render_template("upload.html")
    return ""


with open(CONFIG_PATH, "r") as f:
    cfg = json.loads(f.read())
    FILE_SERVE_PATH = cfg.get("file_serve_path")
    UPLOAD_PASS_HASH = cfg.get("upload_pass_hash")
    app.run(host=cfg.get("host"), port=cfg.get("port"), debug=cfg.get("debug"))
