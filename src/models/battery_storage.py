from src.models.abstract_asset import Asset
from src.config.config import DATASETS

class BatteryStorage(Asset):
    def __init__(self, name):
        self.rating_kw = DATASETS[name]['rating_kw']
        self.rating_kwh = DATASETS[name]['rating_kwh']
        super().__init__(name)