import os, datetime, shutil, subprocess, json
from pathlib import Path
from flask import abort, session
from core.config import BASE_DIR, SERVICES_FILE

TASK_PROGRESS = {}
CANCEL_TASKS = set()
VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov", ".avi", ".m4v", ".webm"
}

class PermissionDenied(Exception):
    pass

def safe_Path(subpath):
    if not subpath:
        subpath = ""

    path = Path(*Path(subpath).parts)

    if path.is_absolute():
        raise PermissionDenied()

    full_path = (BASE_DIR / path).resolve()

    try:
        full_path.relative_to(BASE_DIR)
    except ValueError:
        raise PermissionDenied()

    if session.get("role") == "admin":
        return full_path

    allowed = session.get("allowed", [])
    relative = full_path.relative_to(BASE_DIR)

    for folder in allowed:
        folder = Path(folder)

        if relative == folder or folder in relative.parents:
            return full_path
    raise PermissionDenied()


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

    info = {
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
    if (
        full_Path.is_file()
        and full_Path.suffix.lower() in VIDEO_EXTENSIONS
    ):
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_streams",
                    str(full_Path)
                ],
                capture_output=True,
                text=True
            )
            data = json.loads(result.stdout)
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    width = stream.get("width")
                    height = stream.get("height")

                    if width and height:
                        info["resolution"] = f"{width}x{height}"

                    fps_raw = stream.get("r_frame_rate", "0/1")

                    try:
                        num, den = map(int, fps_raw.split("/"))
                        if den != 0:
                            fps = round(num / den, 2)
                            info["fps"] = f"{fps} FPS"
                    except Exception:
                        pass

                    break
        except Exception:
            pass
    return info


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
                    if task_id in CANCEL_TASKS:
                        TASK_PROGRESS[task_id] = {
                            "status": "cancelled",
                            "progress": TASK_PROGRESS[task_id].get("progress", 0)
                        }

                        try:
                            fdst.close()
                        except:
                            pass

                        try:
                            if destination.exists():
                                destination.unlink()
                        except:
                            pass

                        return
                    
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
                if task_id in CANCEL_TASKS:
                    TASK_PROGRESS[task_id] = {
                        "status": "cancelled",
                        "progress": TASK_PROGRESS[task_id].get("progress", 0)
                    }
                    try:
                        if dst.exists():
                            shutil.rmtree(dst)
                    except:
                        pass

                    return
                relative = Path(root).relative_to(src)
                target_root = dst / relative
                target_root.mkdir(parents=True, exist_ok=True)
                for file in files:

                    if task_id in CANCEL_TASKS:
                        TASK_PROGRESS[task_id] = {
                            "status": "cancelled",
                            "progress": TASK_PROGRESS[task_id].get("progress", 0)
                        }
                        try:
                            if dst.exists():
                                shutil.rmtree(dst)
                        except:
                            pass
                        return

                    source_file = Path(root) / file
                    target_file = target_root / file

                    copy_file(source_file, target_file)

        TASK_PROGRESS[task_id]["progress"] = 100
        TASK_PROGRESS[task_id]["status"] = "completed"

    except Exception as e:
        TASK_PROGRESS[task_id]["status"] = "error"
        TASK_PROGRESS[task_id]["error"] = str(e)


def load_Services():
    if SERVICES_FILE.exists():
        with open(SERVICES_FILE, "r") as f:
            return json.load(f)
    return []


def get_Service_Info(name):
    def run(cmd):
        return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()

    active_State = run(["systemctl", "is-active", name])
    enabled_State = run(["systemctl", "is-enabled", name])
    desc = run(["systemctl", "show", name, "-p", "Description"]).replace("Description=", "")
    pid = run(["systemctl", "show", name, "-p", "MainPID"]).split("=")[-1].strip()

    return {
        "name": name,
        "active": active_State,
        "enabled": enabled_State,
        "description": desc,
        "pid": pid if pid != "0" else "N/A"
    }