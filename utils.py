import os, datetime
from pathlib import Path
from flask import abort
from paths import BASE_DIR

TASK_PROGRESS = {}


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


def get_Dir_Size(path):
    total_Size = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total_Size += entry.stat().st_size
            elif entry.is_dir():
                total_Size += get_Dir_Size(entry.path)
    except (PermissionError, OSError):
        pass
    return total_Size


def format_Size(raw_size):
    for unit in ["Bytes", "KB", "MB", "GB", "TB"]:
        if raw_size < 1024.0:
            return f"{raw_size:.2f} {unit}" if unit != "Bytes" else f"{raw_size} Bytes"
        raw_size /= 1024.0
    return f"{raw_size:.2f} PB"


def get_Item_Info(full_Path):
    stats = full_Path.stat()

    if full_Path.is_dir():
        raw_size = get_Dir_Size(full_Path)
        item_type = "Folder"
    else:
        raw_size = stats.st_size
        item_type = "File"

    return {
        "name": full_Path.name,
        "size": format_Size(raw_size),
        "created": datetime.datetime.fromtimestamp(stats.st_ctime).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "modified": datetime.datetime.fromtimestamp(stats.st_mtime).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "type": item_type,
        "extension": full_Path.suffix if full_Path.is_file() else "N/A",
    }


def save_Uploaded_File(file, destination):
    with open(destination, "wb") as f:
        file.stream.seek(0)

        while True:
            chunk = file.stream.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)


def get_Total_Size(path):
    if path.is_file():
        return path.stat().st_size
    total = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            fp = Path(root) / file
            try:
                total += fp.stat().st_size
            except Exception:
                pass
    return total


def copy_With_Progress(src, dst, task_id):
    total_size = get_Total_Size(src)
    copied_size = 0

    TASK_PROGRESS[task_id] = {"progress": 0, "status": "running"}

    def copy_file(source, destination):
        nonlocal copied_size
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(source, "rb") as fsrc:
            with open(destination, "wb") as fdst:
                while True:
                    chunk = fsrc.read(1024 * 1024)

                    if not chunk:
                        break

                    fdst.write(chunk)
                    copied_size += len(chunk)
                    progress = int((copied_size / total_size) * 100)
                    TASK_PROGRESS[task_id]["progress"] = progress

    try:
        if src.is_file():
            copy_file(src, dst)
        else:
            for root, dirs, files in os.walk(src):
                relative = Path(root).relative_to(src)
                target_root = dst / relative
                target_root.mkdir(parents=True, exist_ok=True)
                for file in files:

                    source_file = Path(root) / file
                    target_file = target_root / file
                    copy_file(source_file, target_file)
        TASK_PROGRESS[task_id]["progress"] = 100
        TASK_PROGRESS[task_id]["status"] = "completed"

    except Exception as e:
        TASK_PROGRESS[task_id]["status"] = "error"
        TASK_PROGRESS[task_id]["error"] = str(e)
