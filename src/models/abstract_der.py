
import pandas as pd
import os
from abc import ABC, abstractmethod
from config.config import DATASETS
from config.paths import FORMATTED_DATA_PATH
# abstract base class

#provides an abstract base class for DER models(batteries, pv generators, etc.)
class AbstractDER(ABC):
    def __init__(self, name):
        self.name = name
        self.df = None 

    def load_data(self):
        formatted_file = os.path.join(
            FORMATTED_DATA_PATH,
            DATASETS[self.name]["formatted_filename"]
        )

        if not os.path.exists(formatted_file):
            raise FileNotFoundError(f"Formatted file not found: {formatted_file}")

        self.df = pd.read_csv(formatted_file, parse_dates=["DateTime"])
        self.df = self.df.sort_values("DateTime").reset_index(drop=True)