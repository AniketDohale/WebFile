import os, shutil
from flask import Flask, render_template, request, redirect, send_from_directory, abort
from pathlib import Path

app = Flask(__name__)
BASE_DIR = Path(r"D:\Media").resolve()

def safe_Path(subpath):
    full_Path = (BASE_DIR / subpath).resolve()
    if not str(full_Path).startswith(str(BASE_DIR)):
        abort(403)
    return full_Path

@app.route("/")
@app.route("/<path:subpath>")
def browse(subpath=""):
    full_Path = safe_Path(subpath)

    if not os.path.exists(full_Path):
        return "Folder not Found", 404

    items = []

    for name in os.listdir(full_Path):
        item_path = os.path.join(full_Path, name)
        items.append({
            "name": name,
            "is_dir": os.path.isdir(item_path)
        })

    items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))

    return render_template(
        "index.html",
        items=items,
        current_path=subpath
    )

@app.route("/upload", methods=["POST"])
def upload():
    subpath = request.form.get("path", "")
    full_Path = safe_Path(subpath)
    
    f = request.files["file"]
    f.save(full_Path / f.filename)
    return redirect(f"/{subpath}" if subpath else "/")


@app.route("/download/<path:filepath>")
def download(filepath):
    full_Path = safe_Path(filepath)

    return send_from_directory(full_Path.parent, full_Path.name, as_attachment=True)


@app.route("/rename", methods=["POST"])
def rename():
    old_path = request.form.get("old_path")
    new_name = request.form.get("new_name")

    full_old_path = safe_Path(old_path)

    if not full_old_path.exists():
        return "File not found", 404

    if not new_name or "/" in new_name or "\\" in new_name:
        return "Invalid Name", 400

    new_path = full_old_path.parent / new_name

    if new_path.exists():
        return "File with this name already exists", 400

    try:
        full_old_path.rename(new_path)
    except Exception as e:
        return f"Error: {e}", 500

    parent = full_old_path.parent.relative_to(BASE_DIR)
    return redirect(f"/{parent}" if str(parent) != "." else "/")


@app.route("/delete", methods=["POST"])
def delete():
    target_path = request.form.get("path")
    full_path = safe_Path(target_path)

    if not full_path.exists():
        return "File not found", 404

    try:
        if full_path.is_file():
            full_path.unlink() 
        elif full_path.is_dir():
            shutil.rmtree(full_path)
    except Exception as e:
        return f"Error: {e}", 500

    parent = full_path.parent.relative_to(BASE_DIR)
    return redirect(f"/{parent}" if str(parent) != "." else "/")

if __name__=="__main__":
    app.run(debug=True)