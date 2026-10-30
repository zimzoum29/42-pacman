from ...game.game import Game, Status
from ..window import Window, Key
from ..button import Action


class EndScreen:

    def __init__(self, window: Window, game: Game) -> None:
        self._window = window
        self._game_score = game.score
        self._game_status = game.status

    def draw(self) -> None:
        ...

    def update(self, keys: list[Key]) -> Action | None:
        ...
