from flask import Flask, request, render_template, send_file
import json
from pathlib import Path
import os

app = Flask(__name__)
CONFIG_PATH = "config.json"


@app.route("/files")
def files():
    files = {
        "a": {
            "b": {
                "c": {
                    "test.html": ""
                }
            }
        },
        "test.py": ""
    }
    return render_template("files.html", files=files)


@app.route("/files/<path:filename>")
def file_path(filename):
    path = Path(filename)
    if path.is_dir():
        files = [(Path(Path(FILE_SERVE_PATH)/path/Path(file)).relative_to(Path(FILE_SERVE_PATH)),
                  file+("/" if Path(Path(FILE_SERVE_PATH)/path/Path(file)).relative_to(Path(FILE_SERVE_PATH)).is_dir() else ""))
                 for file in os.listdir(Path(FILE_SERVE_PATH)/path)]
        print(files)
        return render_template("files.html", files=files, header="/"+filename+"/")
    return send_file(path)


with open(CONFIG_PATH, "r") as f:
    cfg = json.loads(f.read())
    FILE_SERVE_PATH = cfg.get("file_serve_path")
    app.run(host=cfg.get("host"), port=cfg.get("port"), debug=cfg.get("debug"))