from src.models.abstract_asset import Asset

class BatteryStorage(Asset):
    def __init__(self, name, rating_kw, rating_kwh):
        self.rating_kw = rating_kw
        self.rating_kwh = rating_kwh
        super().__init__(name)