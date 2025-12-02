
import pandas as pd
import os
from abc import ABC
from src.config.config import DATASETS, COLUMN_NAMES
from src.config.paths import FORMATTED_DATA_PATH

#provides an abstract base class for assets in a microgrid(batteries, pv generators, etc.)
class Asset(ABC):
    def __init__(self, name):
        self.name = name
        #check if the name exists in the DATASETS config
        if name not in DATASETS:
            raise ValueError(f"Dataset '{name}' not found in configuration.")
        self.df = None 
        #when the object is created, load the data 
        self.load_data()

    def load_data(self):
        #loads the data from the formatted file into the member variable df
        formatted_file_path = os.path.join(
            FORMATTED_DATA_PATH,
            DATASETS[self.name]["formatted_filename"]
        )

        if not os.path.exists(formatted_file_path):
            raise FileNotFoundError(f"Formatted file not found: {formatted_file_path}")

        self.df = pd.read_csv(formatted_file_path, parse_dates=["DateTime"])
        self.df = self.df.sort_values("DateTime").reset_index(drop=True)

    def get_df(self, start=None, end=None):
        #converts start and end to datetime if they are provided
        if start is not None:
            start = pd.to_datetime(start)
        if end is not None:
            end = pd.to_datetime(end)


        if not self.check_dates_exists(start, end):
            raise ValueError("Requested date range is out of bounds.")
        
        df = self.df
        if start:
            df = df[df["DateTime"] >= start]
        if end:
            df = df[df["DateTime"] < end]

        return df
    
    def get_real_power(self, start=None, end=None):
        df = self.get_df(start, end)
        #check if the real power column exists
        if COLUMN_NAMES["real_power"] not in df.columns:
            raise ValueError(f"Real power column '{COLUMN_NAMES['real_power']}' not found in dataset for asset '{self.name}'.")
        return df[COLUMN_NAMES["real_power"]].values
    
    def get_reactive_power(self, start=None, end=None):
        df = self.get_df(start, end)
        #check if the reactive power column exists
        if COLUMN_NAMES["reactive_power"] not in df.columns:
            raise ValueError(f"Reactive power column '{COLUMN_NAMES['reactive_power']}' not found in dataset for asset '{self.name}'.")
        return df[COLUMN_NAMES["reactive_power"]].values
    
    def get_datetime_index(self, start=None, end=None):
        df = self.get_df(start, end)
        if COLUMN_NAMES["datetime"] not in df.columns:
            raise ValueError(f"Datetime column '{COLUMN_NAMES['datetime']}' not found in dataset for asset '{self.name}'.")
        return df[COLUMN_NAMES["datetime"]].values
    
    def check_dates_exists(self, start=None, end=None):
        if start and start < self.df["DateTime"].min():
            return False
        if end and end > self.df["DateTime"].max():
            return False
        return True

