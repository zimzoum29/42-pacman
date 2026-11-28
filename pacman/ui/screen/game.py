import time

import pygame

from ...config import Config
from ...game.game import Game, Status
from ...game.maze import Direction
from ..button import Action, Button
from ..window import BLACK, WHITE, Color, Key, Window
from ...path import ASSET_DIR

HUD_HEIGHT = 0.05
HUD_FONT_SIZE = 36
MARGIN = 0.03
MAX_DT = 0.1

YELLOW: Color = (255, 255, 0)
WALL_COLOR: Color = (33, 33, 222)
BLOCK_COLOR: Color = (20, 20, 120)
GHOST_COLOR: Color = (255, 0, 0)
FRIGHTENED_COLOR: Color = (60, 60, 255)

KEY_DIRECTIONS: dict[Key, Direction] = {
    Key.UP: Direction.UP,
    Key.DOWN: Direction.DOWN,
    Key.LEFT: Direction.LEFT,
    Key.RIGHT: Direction.RIGHT,
}

CELL_SIZE = 76
WALL_THICKNESS = 10
FLOOR_PATH = ASSET_DIR / "floor.png"
WALL_H_PATH = ASSET_DIR / "wall_h.png"
WALL_V_PATH = ASSET_DIR / "wall_v.png"
BLOCK_PATH = ASSET_DIR / "block.png"
BLINKY_PATH = ASSET_DIR / "blinky.png"
CLYDE_PATH = ASSET_DIR / "clyde.png"
PINKY_PATH = ASSET_DIR / "pinky.png"
INKY_PATH = ASSET_DIR / "inky.png"
FRIGHTENED_GHOST_PATH = ASSET_DIR / "frightened_ghost.png"
FRIGHTENED_WHITE_PATH = ASSET_DIR / "frightened_ghost_white.png"
PAUSED_TITLE_PATH = ASSET_DIR / "game_paused.png"
CHEAT_BUBBLE_PATH = ASSET_DIR / "cheat_bubble.png"
PAUSED_TITLE_Y = 0.20
BLINK_START = 3.0
BLINK_PERIOD = 0.25
GHOST_NAMES = ("blinky", "pinky", "inky", "clyde")
GHOST_FRAMES = 2
GHOST_FRAME_TIME = 0.15

DIRECTION_NAMES: dict[Direction, str] = {
    Direction.UP: "up",
    Direction.DOWN: "down",
    Direction.LEFT: "left",
    Direction.RIGHT: "right",
}

ARROW_GAP = 2

FIRST_BUTTON_Y = 0.45
BUTTON_SPACING = 0.03
PAUSE_BUTTONS: tuple[tuple[str, str, Action], ...] = (
    (ASSET_DIR / "back_to_game.png", ASSET_DIR / "back_to_game_active.png", Action.PLAY),
    (ASSET_DIR / "back_to_menu.png",ASSET_DIR / "back_to_menu_active.png", Action.HOME),
    )


class GameScreen:

    def __init__(self, window: Window, config: Config) -> None:
        self._window = window
        self._game = Game(config)
        self._last_time = time.monotonic()
        self._floor_img = window.load_image(FLOOR_PATH)
        self._wall_h_img = window.load_image(WALL_H_PATH)
        self._wall_v_img = window.load_image(WALL_V_PATH)
        self._block_img = window.load_image(BLOCK_PATH)
        self._paused_title = window.load_image(PAUSED_TITLE_PATH)
        self._ghost_imgs = {
            name: {
                d: [window.load_image(
                        ASSET_DIR / f"{name}_{dir_name}_{frame}.png")
                    for frame in range(GHOST_FRAMES)]
                for d, dir_name in DIRECTION_NAMES.items()
            }
            for name in GHOST_NAMES
        }
        self._ghost_facing: dict[str, Direction] = {
            name: Direction.LEFT for name in GHOST_NAMES
        }
        self._anim_time = 0.0
        self._frightened_imgs = {
            color: [window.load_image(
                        ASSET_DIR / f"frightened_{color}_{frame}.png")
                    for frame in range(GHOST_FRAMES)]
            for color in ("blue", "white")
        }
        self._pacman_imgs = {
            d: window.load_image(ASSET_DIR / f"pacman_{name}.png")
            for d, name in DIRECTION_NAMES.items()
        }
        self._arrow_imgs = {
            d: window.load_image(ASSET_DIR / f"arrow_{name}.png")
            for d, name in DIRECTION_NAMES.items()
        }
        self._pause_overlay = window.create_dither_overlay()
        self._load_level()

        self._buttons = [
            Button(window, idle, active, action)
            for idle, active, action in PAUSE_BUTTONS
        ]
        self._selected = 0
        self._cheat_bubble = window.load_image(CHEAT_BUBBLE_PATH)
        game = self._game
        self._cheat_keys = {
            Key.DIGIT_1: game.toggle_immortality,
            Key.DIGIT_2: game.toggle_ghost_freeze,
            Key.DIGIT_3: game.toggle_fast,
            Key.DIGIT_4: game.add_life,
            Key.DIGIT_5: game.skip_level,
        }

    def _load_level(self) -> None:
        self._level = self._game.level
        self._map = self._game.map
        self._compute_layout()
        self._floors = self._build_floors()
        self._walls = self._build_walls()
        self._build_images()

    def _compute_layout(self) -> None:
        window = self._window
        margin = window.ratio_y(MARGIN)
        top = window.ratio_y(HUD_HEIGHT)
        free_w = window.width - 2 * margin
        free_h = window.height - top - margin
        self._cell = min(free_w // self._map.width, free_h // self._map.height)
        self._thick = max(self._cell // 8, 2)
        map_w = self._cell * self._map.width
        map_h = self._cell * self._map.height
        self._origin_x = (window.width - map_w) // 2
        self._origin_y = top + (free_h - map_h) // 2
        self._cell = CELL_SIZE
        self._thick = WALL_THICKNESS

    def _build_walls(self) -> list[tuple[pygame.Surface, int, int]]:
        size = self._cell
        half = self._thick // 2
        h_wall, v_wall = self._wall_h_img, self._wall_v_img

        walls: list[tuple[pygame.Surface, int, int]] = []
        blocks: list[tuple[pygame.Surface, int, int]] = []
        for y, row in enumerate(self._map.cells):
            for x, cell in enumerate(row):
                px, py = self.cell_to_pixel(x, y)
                if cell.is_closed:
                    if self._block_img is not None:
                        blocks.append((self._block_img, px, py))
                    continue
                if h_wall is not None:
                    if cell.north:
                        walls.append((h_wall, px - half, py - half))
                    if cell.south:
                        walls.append((h_wall, px - half, py + size - half))
                if v_wall is not None:
                    if cell.west:
                        walls.append((v_wall, px - half, py - half))
                    if cell.east:
                        walls.append((v_wall, px + size - half, py - half))
        return walls + blocks

    def _build_images(self) -> None:
        cell = self._cell
        self._pacgum_size = max(cell // 6, 2)
        self._super_size = max(cell // 3, 4)
        self._entity_size = cell // 2
        new = self._window.new_image
        self._pacgum_img = new(self._pacgum_size, self._pacgum_size, YELLOW)
        self._super_img = new(self._super_size, self._super_size, YELLOW)
        size = self._entity_size

    def cell_to_pixel(self, x: int, y: int) -> tuple[int, int]:
        return (self._origin_x + x * self._cell,
                self._origin_y + y * self._cell)

    def update(self, keys: list[Key]) -> Action | None:
        for key in keys:
            if key is Key.T:
                return Action.GAME_OVER
            if key is Key.QUIT:
                return Action.QUIT
            if key is Key.ESCAPE:   
                self._game.switch_pause()
                continue
            if key in KEY_DIRECTIONS:
                if self._game.status is Status.PAUSE:
                    match key:
                        case Key.UP:
                            self._move(-1)
                        case Key.DOWN:
                            self._move(1)
                else:
                    self._game.set_direction(KEY_DIRECTIONS[key])
            elif self._game.status is Status.PAUSE and key is Key.ENTER:
                match self._buttons[self._selected].action:
                    case Action.PLAY:
                        self._game.switch_pause()
                    case Action.HOME:
                        return Action.HOME
            elif key is Key.PAUSE:
                self._game.switch_pause()
            elif key is Key.C and self._game.status is Status.PLAYING:
                if self._game.cheat:
                    self._game.toggle_cheat()
                else:
                    self._game.cheat = True
            elif key in self._cheat_keys and self._game.cheat:
                self._cheat_keys[key]()
            

        now = time.monotonic()
        dt = min(now - self._last_time, MAX_DT)
        self._last_time = now
        self._game.update(dt)
        if self._game.status is Status.PLAYING:
            self._anim_time += dt

        if self._game.status in [Status.GAME_OVER, Status.VICTORY]:
            return Action.GAME_OVER
        if self._game.level != self._level:
            self._load_level()
        return None

    def draw(self) -> None:
        self._window.fill(BLACK)
        if self._floor_img is not None:
            for x, y in self._floors:
                self._window.blit(self._floor_img, x, y)
        for image, x, y in self._walls:
            self._window.blit(image, x, y)
        self._draw_pacgums()
        self._draw_ghosts()
        self._draw_pacman()

        if self._game.status is Status.PAUSE:
            self._window.blit(self._pause_overlay, 0, 0)
            if self._paused_title is not None:
                self._window.blit_centered_x(
                    self._paused_title, self._window.ratio_y(PAUSED_TITLE_Y))
            self._draw_buttons()
        if self._game.cheat and self._game.status is Status.PLAYING:
            self._draw_cheat()

    def _draw_pacgums(self) -> None:
        for y, row in enumerate(self._map.cells):
            for x, cell in enumerate(row):
                if cell.pacgum:
                    self._draw_centered(self._pacgum_img, self._pacgum_size, x, y)
                elif cell.super_pacgum:
                    self._draw_centered(self._super_img, self._super_size, x, y)

    def _draw_ghosts(self) -> None:
        frame = int(self._anim_time / GHOST_FRAME_TIME) % GHOST_FRAMES
        frightened_img = self._frightened_image(frame)
        for ghost in self._game.ghosts:
            if not ghost.is_active:
                continue
            if ghost.direction is not None:
                self._ghost_facing[ghost.name] = ghost.direction
            if ghost.frightened:
                image = frightened_img
            else:
                facing = self._ghost_facing[ghost.name]
                image = self._ghost_imgs[ghost.name][facing][frame]
            if image is not None:
                gx, gy = ghost.position
                self._blit_center(image, *self._cell_center(gx, gy))

    def _draw_centered(self, image: pygame.Surface, size: int,x: float, y: float) -> None:
        offset = (self._cell - size) // 2
        px = self._origin_x + x * self._cell + offset
        py = self._origin_y + y * self._cell + offset
        self._window.blit(image, int(px), int(py))

    def _build_floors(self) -> list[tuple[int, int]]:
        floors: list[tuple[int, int]] = []
        for y, row in enumerate(self._map.cells):
            for x, cell in enumerate(row):
                if not cell.is_closed:
                    floors.append(self.cell_to_pixel(x, y))
        return floors

    def _draw_pacman(self) -> None:
        pacman = self._game.pacman
        facing = pacman.direction or pacman.last_direction
        cx, cy = self._cell_center(*pacman.position)

        sprite = self._pacman_imgs[facing]
        if sprite is not None:
            self._blit_center(sprite, cx, cy)

        wanted = pacman.wanted or facing
        arrow = self._arrow_imgs[wanted]
        if arrow is None:
            return
        reach_x = (sprite.get_width() if sprite else 0) // 2
        reach_y = (sprite.get_height() if sprite else 0) // 2
        dist_x = reach_x + arrow.get_width() // 2 + ARROW_GAP
        dist_y = reach_y + arrow.get_height() // 2 + ARROW_GAP
        self._blit_center(arrow, cx + wanted.dx * dist_x, cy + wanted.dy * dist_y)

    def _cell_center(self, x: float, y: float) -> tuple[float, float]:
        return (self._origin_x + (x + 0.5) * self._cell,
                self._origin_y + (y + 0.5) * self._cell)

    def _blit_center(self, image: pygame.Surface, cx: float, cy: float) -> None:
        self._window.blit(image, int(cx - image.get_width() / 2), int(cy - image.get_height() / 2))

    def _draw_buttons(self) -> None:
        y = self._window.ratio_y(FIRST_BUTTON_Y)
        spacing = self._window.ratio_y(BUTTON_SPACING)
        for index, button in enumerate(self._buttons):
            plate = button.plate(index == self._selected)
            if plate is not None:
                x = (self._window.width - plate.get_width()) // 2
                self._window.blit(plate, x, y)
            y += button.height + spacing

    def _move(self, step: int) -> None:
        self._selected = (self._selected + step) % len(self._buttons)

    def _frightened_image(self, frame: int) -> pygame.Surface:
        time_left = self._game.frightened_time
        color = "blue"
        if time_left <= BLINK_START and int(time_left / BLINK_PERIOD) % 2 == 0:
            color = "white"
        return self._frightened_imgs[color][frame]

    def _draw_cheat(self):
        bubble = self._cheat_bubble
        x = (self._origin_x - bubble.get_width()) // 2
        map_h = self._map.height * self._cell
        y = self._origin_y + (map_h - bubble.get_height()) // 2
        self._window.blit(bubble, max(x, 0), y)
    