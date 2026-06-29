import platform
from pathlib import Path

SYSTEM = platform.system()

# Project Root
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Data Directory
DATA_DIR = PROJECT_DIR / "data"

# JSON Files
USERS_FILE = DATA_DIR / "users.json"
SERVICES_FILE = DATA_DIR / "services.json"

# Base Directory
if SYSTEM == "Windows":
    BASE_DIR = Path(r"D:\Media").resolve()
else:
    BASE_DIR = Path.home().resolve()


# print("*" * 80)
# print("SYSTEM:", SYSTEM)
# print("BASE_DIR:", BASE_DIR)

# if SYSTEM != "Windows":
#     print("TEMP_DIR:", TEMP_DIR)
# else:
#     print("Using System Default Temp", tempfile.gettempdir())
# print("*" * 80)
