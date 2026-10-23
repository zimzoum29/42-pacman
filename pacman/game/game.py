import random
from enum import Enum, auto

from ..config import Config
from .entities import Ghost, Blinky, Inky, Pinky, Clyde, GhostMode, Pacman
from .maze import Direction, Map

MAP_WIDTH = 20
MAP_HEIGHT = 15
LEVEL_COUNT = 10
RANDOM_SEED = 0

PACMAN_SPEED = 6.0
GHOST_SPEED = 4.0
FAST_FACTOR = 2.0

FRIGHTENED_DURATION = 8.0
GHOST_RESPAWN_DELAY = 5.0
HIT_DISTANCE = 0.5


class Status(Enum):
    PLAYING = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class Game:

    def __init__(self, config: Config) -> None:
        self.config = config
        self.score = 0
        self.lives = config.lives
        self.status = Status.PLAYING
        self.new_mode: GhostMode | None = GhostMode.SCATTER
        self.frightened_time = 0.0
        self.fast = False
        self._rng = random.Random()
        self._start_level(1)

    def _start_level(self, level: int) -> None:
        self.level = level
        seed = self.config.seed if level == 1 else RANDOM_SEED
        self.map = Map(MAP_WIDTH, MAP_HEIGHT, seed)
        self.spawn = self.map.spawn_cell()
        self._init_entities()
        self.pacgums_left = self.map.count_pacgums()
        self.time_left = float(self.config.level_max_time)
        self.frightened_time = 0.0

    def _init_entities(self) -> None:
        self.pacman = Pacman(*self.spawn, PACMAN_SPEED)

        self.pinky = Pinky(*self.map.corners()[0], GHOST_SPEED,
                           self._rng, self.pacman)
        self.blinky = Blinky(*self.map.corners()[1], GHOST_SPEED,
                             self._rng, self.pacman)
        self.clyde = Clyde(*self.map.corners()[2], GHOST_SPEED,
                           self._rng, self.pacman)
        self.inky = Inky(*self.map.corners()[3], GHOST_SPEED,
                         self._rng, self.pacman, self.blinky)

        self.ghosts = [
            self.pinky,
            self.blinky,
            self.clyde,
            self.inky
        ]

    def _next_level(self) -> None:
        if self.level >= LEVEL_COUNT:
            self.status = Status.VICTORY
        else:
            self._start_level(self.level + 1)

    def set_direction(self, direction: Direction) -> None:
        """The player wants to go this way (applied as soon as possible)."""
        self.pacman.wanted = direction

    def update(self, dt: float) -> None:
        if self.status is not Status.PLAYING:
            return
        level = self.level

        self._move_pacman(dt)
        if self.level != level or self.status is not Status.PLAYING:
            return
        self._move_ghosts(dt)
        if self.new_mode:
            self.new_mode = None
        self._check_collisions()
        self._update_timers(dt)

    def _move_pacman(self, dt: float) -> None:
        factor = FAST_FACTOR if self.fast else 1.0
        self.pacman.speed = PACMAN_SPEED * factor
        level = self.level
        for x, y in self.pacman.update(dt, self.map):
            self._eat(x, y)
            if self.level != level or self.status is not Status.PLAYING:
                return

    def _eat(self, x: int, y: int) -> None:
        cell = self.map.cells[y][x]
        if cell.pacgum:
            cell.pacgum = False
            self.score += self.config.points_per_pacgum
            self.pacgums_left -= 1
        elif cell.super_pacgum:
            cell.super_pacgum = False
            self.score += self.config.points_per_super_pacgum
            self.pacgums_left -= 1
            self.frightened_time = FRIGHTENED_DURATION
            self.new_mode = GhostMode.FRIGHTENED
        if self.pacgums_left == 0:
            self._next_level()

    def _move_ghosts(self, dt: float) -> None:
        for ghost in self.ghosts:
            if ghost.is_active:
                ghost.update(dt, self.map, self.new_mode)

    def _check_collisions(self) -> None:
        px, py = self.pacman.position
        for ghost in self.ghosts:
            if not ghost.is_active:
                continue
            gx, gy = ghost.position
            if abs(px - gx) < HIT_DISTANCE and abs(py - gy) < HIT_DISTANCE:
                if self.frightened_time > 0:
                    self._eat_ghost(ghost)
                else:
                    self.lose_life()
                    return

    def _eat_ghost(self, ghost: Ghost) -> None:
        self.score += self.config.points_per_ghost
        ghost.go_home()
        ghost.respawn_time = GHOST_RESPAWN_DELAY

    def _update_timers(self, dt: float) -> None:
        self.frightened_time = max(0.0, self.frightened_time - dt)
        for ghost in self.ghosts:
            if not ghost.is_active:
                ghost.respawn_time = max(0.0, ghost.respawn_time - dt)
        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = float(self.config.level_max_time)
            self.lose_life()

    def lose_life(self) -> None:
        self.lives -= 1
        if self.lives <= 0:
            self.status = Status.GAME_OVER
            return
        self.pacman.place(*self.spawn)
        for ghost in self.ghosts:
            ghost.go_home()
