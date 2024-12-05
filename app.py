from flask import Flask, request, render_template, send_file
import json
from pathlib import Path
import os

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


with open(CONFIG_PATH, "r") as f:
    cfg = json.loads(f.read())
    FILE_SERVE_PATH = cfg.get("file_serve_path")
    app.run(host=cfg.get("host"), port=cfg.get("port"), debug=cfg.get("debug"))
