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

CHASE_DURATION = 10.0
SCATTER_DURATION = 5.0
FRIGHTENED_DURATION = 8.0
GHOST_RESPAWN_DELAY = 5.0
HIT_DISTANCE = 0.42


class Status(Enum):
    PLAYING = auto()
    PAUSE = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class Game:

    def __init__(self, config: Config) -> None:
        self.config = config
        self.score = 0
        self.lives = config.lives
        self.status = Status.PLAYING
        self.frightened_time = FRIGHTENED_DURATION
        self.current_mode = GhostMode.CHASE
        self.mode_timer = CHASE_DURATION
        self._rng = random.Random()
        self._start_level(1)
        self._init_cheat_variables()

    def _init_cheat_variables(self) -> None:
        self.player_immortality: bool = False
        self.ghosts_frozen = False
        self.fast = False

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

        pinky = Pinky(*self.map.corners()[0], GHOST_SPEED,
                      self._rng, self.pacman)
        blinky = Blinky(*self.map.corners()[1], GHOST_SPEED,
                        self._rng, self.pacman)
        clyde = Clyde(*self.map.corners()[2], GHOST_SPEED,
                      self._rng, self.pacman)
        inky = Inky(*self.map.corners()[3], GHOST_SPEED,
                    self._rng, self.pacman, blinky)

        self.ghosts: list[Ghost] = [
            pinky,
            blinky,
            clyde,
            inky
        ]

    def _next_level(self) -> None:
        if self.level >= LEVEL_COUNT:
            self.status = Status.VICTORY
        else:
            self._start_level(self.level + 1)

    def set_direction(self, direction: Direction) -> None:
        self.pacman.wanted = direction

    def switch_pause(self) -> None:
        match self.status:
            case Status.PLAYING:
                self.status = Status.PAUSE
            case Status.PAUSE:
                self.status = Status.PLAYING

    def update(self, dt: float) -> None:
        if self.status is not Status.PLAYING:
            return
        level = self.level

        self._check_collisions()
        self._move_pacman(dt)
        if self.level != level or self.status is not Status.PLAYING:
            return
        self._update_timers(dt)
        self._update_ghost_modes()
        self._move_ghosts(dt)

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
        if self.pacgums_left == 0:
            self._next_level()

    def _check_collisions(self) -> None:
        if self.player_immortality is True and self.frightened_time == 0.0:
            return
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
        if self.frightened_time > 0.0:
            self.frightened_time = max(0.0, self.frightened_time - dt)
        else:
            self.mode_timer = max(0.0, self.mode_timer - dt)
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

    def _switch_mode(self) -> GhostMode:
        match self.current_mode:
            case GhostMode.CHASE:
                self.current_mode = GhostMode.SCATTER
                self.mode_timer = SCATTER_DURATION
                return GhostMode.SCATTER
            case _:
                self.current_mode = GhostMode.CHASE
                self.mode_timer = CHASE_DURATION
                return GhostMode.CHASE

    def _update_ghost_modes(self) -> None:
        if self.frightened_time > 0:
            mode = GhostMode.FRIGHTENED
        elif self.mode_timer == 0.0:
            mode = self._switch_mode()
        else:
            mode = self.current_mode

        for ghost in self.ghosts:
            ghost.set_mode(mode)

    def _move_ghosts(self, dt: float) -> None:
        if self.ghosts_frozen:
            return
        for ghost in self.ghosts:
            if ghost.is_active:
                ghost.update(dt, self.map)
