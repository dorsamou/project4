from src.models.abstract_asset import Asset
from src.config.config import DATASETS

class BuildingLoad(Asset):
    def __init__(self, name):
        self.cal_real = DATASETS[name]['cal_real']
        self.cal_reactive = DATASETS[name]['cal_reactive']
        super().__init__(name)
    def get_load_profile(self, start=None, end=None):
        real_power = self.get_real_power(start, end) 
        return real_power