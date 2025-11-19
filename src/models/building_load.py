from src.models.abstract_asset import Asset

class BuildingLoad(Asset):
    def __init__(self, name, cal_real=1.0, cal_reactive=1.0):
        self.cal_real = cal_real
        self.cal_reactive = cal_reactive
        super().__init__(name)