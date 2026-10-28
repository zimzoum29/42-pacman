import pygame

from ..button import Action
from ..window import TRANSPARENT, BLACK, YELLOW, BLUE, DARK_BLUE, Key, Window
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
        self._row_bg_image = None

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
        rect_y_offset = int((rect_h - size) * 1.5)

        padding = 6
        inner_h = rect_h - (padding * 2)
        rank_rect_w = int(inner_h * 1.6)
        score_rect_w = 260
        name_margin_left = 25

        # Récupère l'image pré-calculée (0 calcul de pixel pendant la boucle !)
        row_bg = self._get_row_bg_image(size)

        step = self._window.ratio_y(ROW_SPACING)
        for rank, (name, score) in enumerate(self._rows, start=1):
            rect_x = (self._window.width - rect_w) // 2
            rect_y = y - rect_y_offset

            # 1. Affiche l'image complète de la boîte d'un seul coup (équivalent win.put_image)
            self._window.blit(row_bg, rect_x, rect_y)

            # 2. Texte du Rang (à gauche)
            rank_rect_x = rect_x + padding
            self._window.text_centered_in_rect(
                f"{rank}", rank_rect_x, rank_rect_w, y, size, YELLOW
            )

            # 3. Texte du Nom
            name_x = rank_rect_x + rank_rect_w + name_margin_left
            self._window.text_at(name, name_x, y, size, YELLOW)

            # 4. Texte du Score (à droite)
            score_rect_x = rect_x + rect_w - padding - score_rect_w
            self._window.text_centered_in_rect(
                f"{score} pts", score_rect_x, score_rect_w, y, size, YELLOW
            )

            y += step

    def _get_row_bg_image(self, size: int) -> pygame.Surface:
        """Génère l'image de la ligne (grand rect + 2 badges) une seule fois et la garde en cache."""
        if getattr(self, "_row_bg_image", None) is not None:
            return self._row_bg_image

        rect_w = 1000
        rect_h = int(size * 1.2)
        rect_radius = 12

        padding = 6
        inner_h = rect_h - (padding * 2)
        inner_radius = max(4, rect_radius - padding)
        rank_rect_w = int(inner_h * 1.6)
        score_rect_w = 260

        # 1. Créer une image vierge de la taille d'une ligne (équivalent mlx.new_image)
        bg_img = self._window.new_image(rect_w, rect_h, TRANSPARENT)

        # 2. Dessiner le grand rectangle bleu (en coordonnées locales 0, 0)
        self._window.draw_rounded_rect(0, 0, rect_w, rect_h, rect_radius, BLUE, surface=bg_img)

        # 3. Dessiner le badge de rang à gauche (en coordonnées locales)
        self._window.draw_rounded_rect(
            padding, padding, rank_rect_w, inner_h, inner_radius, DARK_BLUE, surface=bg_img
        )

        # 4. Dessiner le badge de score à droite (en coordonnées locales)
        score_local_x = rect_w - padding - score_rect_w
        self._window.draw_rounded_rect(
            score_local_x, padding, score_rect_w, inner_h, inner_radius, DARK_BLUE, surface=bg_img
        )

        self._row_bg_image = bg_img
        return self._row_bg_image
