import os

# paths.py inside project4/src/config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # project4/src/config/paths.py -> project4/src -> project4
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw") # project4/data/raw
FORMATTED_DATA_PATH = os.path.join(BASE_DIR, "data", "formatted") # project4/data/formatted