from .maze import Map
from ..config import Config

class Game:

    def __init__(self, map: Map, config: Config):
        self.map = map
        self.config = config
        self.level = 1

    