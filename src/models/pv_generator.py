from src.models.abstract_asset import Asset

class PVGenerator (Asset):
    def __init__(self, name):
        super().__init__(name)