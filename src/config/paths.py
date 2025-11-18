import os

# paths.py inside project4/src/config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
FORMATTED_DATA_PATH = os.path.join(BASE_DIR, "data", "formatted")