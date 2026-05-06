import os, shutil
from flask import Flask, render_template, request, redirect, send_from_directory, abort, flash
from pathlib import Path

app = Flask(__name__)
app.secret_key = "super_secret_key_for_session"
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
        flash("Folder Not Found")
        return redirect("/")

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
    return render_template("index.html", items=items, current_path=str(Path(subpath)).replace("\\", "/"))

@app.route("/upload", methods=["POST"])
def upload():
    subpath = request.form.get("path", "")
    full_Path = safe_Path(subpath)

    if 'file' not in request.files:
        flash("No file part")
        return redirect(request.referrer)
    
    f = request.files["file"]
    if f.filename == '':
        flash("No File Selected")
        return redirect(request.referrer)
    
    filename = Path(f.filename).name
    f.save(full_Path / filename)
    flash(f"Uploaded: {filename}")
    return redirect(f"/{subpath}" if subpath else "/")


@app.route("/download/<path:filepath>")
def download(filepath):
    full_Path = safe_Path(filepath)

    if not full_Path.exists() or not full_Path.is_file():
        flash("Folder Not Found")
        return redirect("/")
    return send_from_directory(directory=full_Path.parent, path=full_Path.name, as_attachment=True)


@app.route("/rename", methods=["POST"])
def rename():
    old_Path = request.form.get("old_path")
    new_Name = request.form.get("new_name")
    full_old_Path = safe_Path(old_Path)

    if not full_old_Path.exists():
        flash("File Not Found")
        return redirect(request.referrer)

    if not new_Name or "/" in new_Name or "\\" in new_Name:
        flash("Nothing Changed")
        return redirect(request.referrer)

    new_Path = full_old_Path.parent / new_Name

    if new_Path.exists():
        flash("Name already Exists")
        return redirect(request.referrer)

    try:
        full_old_Path.rename(new_Path)
        flash("Renamed Successfully!")
    except Exception as e:
        flash(f"Error: {e}")

    parent = full_old_Path.parent.relative_to(BASE_DIR)
    return redirect(f"/{parent}" if str(parent) != "." else "/")


@app.route("/delete", methods=["POST"])
def delete():
    target_path = request.form.get("path")
    full_Path = safe_Path(target_path)
    
    if full_Path == BASE_DIR:
        flash("Cannot Delete Root")
        return redirect("/")

    try:
        if full_Path.is_file():
            full_Path.unlink() 
        elif full_Path.is_dir():
            shutil.rmtree(full_Path)
        flash("Item Deleted")
    except Exception as e:
        flash(f"Error: {e}")

    parent = full_Path.parent.relative_to(BASE_DIR)
    return redirect(f"/{parent}" if str(parent) != "." else "/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001, debug=True)