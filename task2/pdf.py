class ItemPDF:
    def __init__(self, tile):
        self.tile = tile


    def compute_weight(self, surface_weight=1, volume_weight=10):
        tile = self.tile
        surface = 2 * (tile[0] * tile[1] + tile[0] * tile[2] + tile[1] * tile[2])
        volume = tile[0] * tile[1] * tile[2]
        return  volume
