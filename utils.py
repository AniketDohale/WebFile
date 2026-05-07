import os
import datetime
from pathlib import Path
from flask import abort
from paths import BASE_DIR


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
