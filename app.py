import os, shutil
from flask import Flask, render_template, request, redirect, send_from_directory, abort
from pathlib import Path

app = Flask(__name__)
BASE_DIR = Path(r"D:\Media").resolve()
# BASE_DIR = Path("/home/raspberry_cli").resolve()

def safe_Path(subpath):
    if not subpath:
        return BASE_DIR

    path = Path(subpath)

    if path.is_absolute():
        abort(403)

    full_Path = (BASE_DIR / path).resolve()

    try:
        full_Path.relative_to(BASE_DIR)
    except ValueError:
        abort(403)
    return full_Path


@app.route("/")
@app.route("/<path:subpath>")
def browse(subpath=""):
    full_Path = safe_Path(subpath)

    if not full_Path.exists():
        return "Folder Not Found", 404

    items = []

    for item in full_Path.iterdir():
        try:
            items.append({
                "name": item.name,
                "is_dir": item.is_dir()
            })
        except Exception:
            continue

    items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

    return render_template(
        "index.html",
        items=items,
        current_path=str(Path(subpath)).replace("\\", "/")
    )

@app.route("/upload", methods=["POST"])
def upload():
    subpath = request.form.get("path", "")
    full_Path = safe_Path(subpath)
    
    f = request.files["file"]
    filename = Path(f.filename).name
    f.save(full_Path / filename)
    return redirect(f"/{subpath}" if subpath else "/")


@app.route("/download/<path:filepath>")
def download(filepath):
    full_Path = safe_Path(filepath)

    if not full_Path.exists() or not full_Path.is_file():
        return "File Not Found", 404

    return send_from_directory(directory=full_Path.parent, path=full_Path.name, as_attachment=True)


@app.route("/rename", methods=["POST"])
def rename():
    old_path = request.form.get("old_path")
    new_name = request.form.get("new_name")

    if not old_path:
        return "Error: No File Path Provided..", 400

    full_old_path = safe_Path(old_path)

    if not full_old_path.exists():
        return "File Not Found", 404

    if not new_name or "/" in new_name or "\\" in new_name:
        return "Invalid Name", 400

    new_path = full_old_path.parent / new_name

    if new_path.exists():
        return "File with this Name already Exists", 400

    try:
        full_old_path.rename(new_path)
    except Exception as e:
        return f"Error: {e}", 500

    parent = full_old_path.parent.relative_to(BASE_DIR)
    return redirect(f"/{parent}" if str(parent) != "." else "/")


@app.route("/delete", methods=["POST"])
def delete():
    target_path = request.form.get("path")
    full_Path = safe_Path(target_path)

    if not full_Path.exists():
        return "File Not Found", 404
    
    if full_Path == BASE_DIR:
        return "Cannot Delete Root Folder", 400

    try:
        if full_Path.is_file():
            full_Path.unlink() 
        elif full_Path.is_dir():
            shutil.rmtree(full_Path)
    except Exception as e:
        return f"Error: {e}", 500

    parent = full_Path.parent.relative_to(BASE_DIR)
    return redirect(f"/{parent}" if str(parent) != "." else "/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001, debug=True)