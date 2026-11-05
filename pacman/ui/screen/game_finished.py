from ...game.game import Game, Status
from ..window import Window, Key
from ..button import Action


class EndScreen:

    def __init__(self, window: Window, game: Game) -> None:
        self._window = window
        self._game_score = game.score
        self._game_status = game.status

    def update(self, keys: list[Key]) -> Action | None:
        ...

    def draw(self) -> None:
        ...

    def _draw_victory(self) -> None:
        ...

    def _draw_defeat(self) -> None:
        ...

    def _draw_name_input(self) -> None:
        ...


class TextBar:

    def __init__(self,
                 window: Window,
                 w: int,
                 h: int,
                 x: int,
                 y: int,
                 max_characters: int,
                 authorized_characters: str) -> None:
        ...

    def update(self) -> None:
        ...

    def draw(self) -> None:
        ...
