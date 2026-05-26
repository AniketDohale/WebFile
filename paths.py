import platform
from pathlib import Path

SYSTEM = platform.system()

SERVICES_FILE = Path("services.json")

if SYSTEM == "Windows":
    BASE_DIR = Path(r"D:\Media").resolve()

elif SYSTEM == "Linux":
    BASE_DIR = Path.home().resolve()


# print("*" * 80)
# print("SYSTEM:", SYSTEM)
# print("BASE_DIR:", BASE_DIR)

# if SYSTEM != "Windows":
#     print("TEMP_DIR:", TEMP_DIR)
# else:
#     print("Using System Default Temp", tempfile.gettempdir())
# print("*" * 80)
