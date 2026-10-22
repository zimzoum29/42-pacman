from ..button import Action
from ..window import WHITE, YELLOW, BLUE, DARK_BLUE, Key, Window
from ...path import ASSET_DIR

BACKGROUND_PATH = ASSET_DIR / "leaderboard_bg.png"

TITLE = "LEADERBOARD"
TITLE_Y = 0.10

TITLE_FONT_SIZE = 100
ROW_FONT_SIZE = 45
FIRST_ROW_Y = 0.20
ROW_SPACING = 0.07

MAX_ROWS = 10


class LeaderboardScreen:
    ...

    def __init__(self, window: Window, scores: dict[str, int]) -> None:
        self._window = window
        self._background = window.load_image(BACKGROUND_PATH)
        self._rows = sorted(scores.items(),
                            key=lambda row: row[1],
                            reverse=True)[:MAX_ROWS]

    def update(self, keys: list[Key]) -> None | Action:
        for key in keys:
            if key is Key.QUIT:
                return Action.QUIT
            if key in (Key.ESCAPE, Key.ENTER):
                return Action.HOME
        return None

    def draw(self) -> None:
        self._draw_background()
        self._draw_rows()

    def _draw_background(self) -> None:
        self._window.fill()
        if self._background is not None:
            self._window.blit_centered(self._background)

    def _draw_rows(self) -> None:
        size = ROW_FONT_SIZE
        y = self._window.ratio_y(FIRST_ROW_Y)
        if not self._rows:
            self._window.text_centered("NO SCORE YET", y, size, YELLOW)
            return

        rect_w = 1000
        rect_h = int(size * 1.2)
        rect_radius = 12
        rect_y_offset = int((rect_h - size) * 1.5)

        # Paramètres des petits rectangles internes (rang à gauche, score à droite)
        padding = 6
        inner_h = rect_h - (padding * 2)
        inner_radius = max(4, rect_radius - padding)

        rank_rect_w = int(inner_h * 1.6)   # Largeur du badge de rang
        score_rect_w = 300                 # Largeur fixe du badge de score à droite
        name_margin_left = 25              # Espace entre le badge de rang et le nom

        step = self._window.ratio_y(ROW_SPACING)
        for rank, (name, score) in enumerate(self._rows, start=1):
            rect_x = (self._window.width - rect_w) // 2
            rect_y = y - rect_y_offset
            inner_y = rect_y + padding

            # 1. Grand rectangle bleu principal
            self._window.draw_rounded_rect(
                rect_x, rect_y, rect_w, rect_h, rect_radius, BLUE
            )

            # 2. Petit rectangle bleu foncé à gauche (Rang)
            rank_rect_x = rect_x + padding
            self._window.draw_rounded_rect(
                rank_rect_x, inner_y, rank_rect_w, inner_h, inner_radius, DARK_BLUE
            )
            self._window.text_centered_in_rect(
                f"{rank}", rank_rect_x, rank_rect_w, y, size, YELLOW
            )

            # 3. Nom du joueur (aligné à gauche après le badge de rang)
            name_x = rank_rect_x + rank_rect_w + name_margin_left
            self._window.text_at(name, name_x, y, size, YELLOW)

            # 4. Petit rectangle bleu foncé à droite (Score)
            score_rect_x = rect_x + rect_w - padding - score_rect_w
            self._window.draw_rounded_rect(
                score_rect_x, inner_y, score_rect_w, inner_h, inner_radius, DARK_BLUE
            )
            self._window.text_centered_in_rect(
                f"{score}", score_rect_x, score_rect_w, y, size, YELLOW
            )

            y += step
