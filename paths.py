import os
import platform
import tempfile
from pathlib import Path

SYSTEM = platform.system()

if SYSTEM == "Windows":
    BASE_DIR = Path(r"D:\Media").resolve()

else:
    BASE_DIR = Path("/home/raspberry_cli").resolve()

TEMP_DIR = BASE_DIR / ".tmp"

BASE_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

os.environ["TMPDIR"] = str(TEMP_DIR)
os.environ["TEMP"] = str(TEMP_DIR)
os.environ["TMP"] = str(TEMP_DIR)

tempfile.tempdir = str(TEMP_DIR)