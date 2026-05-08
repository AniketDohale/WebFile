import os
import platform
import tempfile
from pathlib import Path

SYSTEM = platform.system()

if SYSTEM == "Windows":
    BASE_DIR = Path(r"D:\Media").resolve()

elif SYSTEM == "Linux":
    BASE_DIR = Path.home().resolve()

    TEMP_DIR = BASE_DIR / ".tmp"
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    os.environ["TMPDIR"] = str(TEMP_DIR)
    os.environ["TEMP"] = str(TEMP_DIR)
    os.environ["TMP"] = str(TEMP_DIR)

    tempfile.tempdir = str(TEMP_DIR)

print("*" * 80)
print("SYSTEM:", SYSTEM)
print("BASE_DIR:", BASE_DIR)

if SYSTEM != "Windows":
    print("TEMP_DIR:", TEMP_DIR)
else:
    print("Using System Default Temp", tempfile.gettempdir())
print("*" * 80)
