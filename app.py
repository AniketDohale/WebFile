import shutil
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_from_directory,
    abort,
    flash,
    session,
)

from pathlib import Path
from paths import BASE_DIR
from utils import safe_Path, get_Item_Info, save_Uploaded_File

app = Flask(__name__)

app.secret_key = "super_secret_key_for_session"


@app.route("/")
@app.route("/<path:subpath>")
def browse(subpath=""):
    full_Path = safe_Path(subpath)

    if not full_Path.exists():
        flash("Folder Not Found")
        return redirect("/")

    url_hidden_param = request.args.get("hidden")
    if url_hidden_param is not None:
        session["show_hidden"] = url_hidden_param == "true"
    show_Hidden = session.get("show_hidden", False)

    items = []

    for item in full_Path.iterdir():
        if not show_Hidden and item.name.startswith("."):
            continue

        try:
            items.append({"name": item.name, "is_dir": item.is_dir()})
        except Exception:
            continue

    items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
    return render_template(
        "index.html",
        items=items,
        current_path=str(Path(subpath)).replace("\\", "/"),
        show_Hidden=show_Hidden,
    )


@app.route("/upload", methods=["POST"])
def upload():
    subpath = request.form.get("path", "")
    full_Path = safe_Path(subpath)

    if "file" not in request.files:
        return "No File Part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No File Selected", 400

    filename = Path(file.filename).name
    destination = full_Path / filename

    if destination.exists():
        return "File Already Exists", 400

    try:
        save_Uploaded_File(file, destination)
        flash(f"Uploaded: {filename}")
        return "OK", 200
    except Exception as e:
        return str(e), 500


@app.route("/download/<path:filepath>")
def download(filepath):
    full_Path = safe_Path(filepath)

    if not full_Path.exists() or not full_Path.is_file():
        flash("Folder Not Found")
        return redirect("/")
    return send_from_directory(
        directory=full_Path.parent, path=full_Path.name, as_attachment=True
    )


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
    target_path = f"/{parent}" if str(parent) != "." else "/"
    return redirect(target_path)


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
    target_path = f"/{parent}" if str(parent) != "." else "/"
    return redirect(target_path)


@app.route("/view/<path:filepath>")
def view(filepath):
    full_Path = safe_Path(filepath)

    if not full_Path.exists() or not full_Path.is_file():
        abort(404)
    return send_from_directory(
        directory=full_Path.parent, path=full_Path.name, as_attachment=False
    )


@app.route("/create-file", methods=["POST"])
def create_File():
    subpath = request.form.get("path", "")
    file_Name = request.form.get("file_name")

    if not file_Name:
        flash("File Name is Required")
        return redirect(request.referrer)

    full_path = safe_Path(subpath) / file_Name

    try:
        full_path.touch(exist_ok=False)
        flash(f"File '{file_Name}' Created.")
    except FileExistsError:
        flash("File Already Exists.")
    except Exception as e:
        flash(f"Error: {e}")

    target_url = f"/{subpath}" if subpath else "/"
    return redirect(target_url)


@app.route("/create-folder", methods=["POST"])
def create_Folder():
    subpath = request.form.get("path", "")
    folder_Name = request.form.get("folder_name")

    if not folder_Name:
        flash("Folder Name is Required")
        return redirect(request.referrer)

    full_path = safe_Path(subpath) / folder_Name

    try:
        full_path.mkdir(exist_ok=False)
        flash(f"Folder '{folder_Name}' Created.")
    except FileExistsError:
        flash("Folder Already Exists.")
    except Exception as e:
        flash(f"Error: {e}")

    target_url = f"/{subpath}" if subpath else "/"
    return redirect(target_url)


@app.route("/info/<path:filepath>")
def get_info(filepath):
    full_Path = safe_Path(filepath)
    if not full_Path.exists():
        return {"error": "File Not Found"}, 404
    return get_Item_Info(full_Path)


@app.route("/copy", methods=["POST"])
def copy():
    path = request.form.get("path")
    if safe_Path(path).exists():
        session["clipboard"] = path
        session["clipboard_mode"] = "copy"
        flash(f"Copied to Clipboard")
    return redirect(request.referrer)


@app.route("/cut", methods=["POST"])
def cut():
    path = request.form.get("path")
    if safe_Path(path).exists():
        session["clipboard"] = path
        session["clipboard_mode"] = "cut"
        flash("Ready to Move")
    return redirect(request.referrer)


@app.route("/paste", methods=["POST"])
def paste():
    source_Path = session.get("clipboard")
    mode = session.get("clipboard_mode", "copy")
    dest_Folder = safe_Path(request.form.get("path", ""))

    if not source_Path:
        flash("Clipboard is Empty")
        return redirect(request.referrer)

    full_Source = safe_Path(source_Path)
    destination = dest_Folder / full_Source.name

    if destination.exists():
        destination = dest_Folder / f"{full_Source.stem}_copy{full_Source.suffix}"

    try:
        if mode == "cut":
            shutil.move(str(full_Source), str(destination))
            session.pop("clipboard", None)
            session.pop("clipboard_mode", None)
            flash(f"Moved '{full_Source.name}' Successfully")
        else:
            if full_Source.is_dir():
                shutil.copytree(full_Source, destination)
            else:
                shutil.copy2(full_Source, destination)
            flash(f"Copied '{full_Source.name}' Successfully")
    except Exception as e:
        flash(f"Error: {e}")
    return redirect(request.referrer)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
