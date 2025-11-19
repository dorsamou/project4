
import pandas as pd
import os
from abc import ABC, abstractmethod
from src.config.config import DATASETS
from src.config.paths import FORMATTED_DATA_PATH
# abstract base class

#provides an abstract base class for assets in a microgrid(batteries, pv generators, etc.)
class Asset(ABC):
    def __init__(self, name):
        self.name = name
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

    def get_data(self, start=None, end=None):
        df = self.df
        if start:
            df = df[df["DateTime"] >= start]
        if end:
            df = df[df["DateTime"] <= end]
        return df

