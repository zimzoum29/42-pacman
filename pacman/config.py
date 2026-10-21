import json


class ConfigError(Exception):
    pass


class Config:

    default: dict = {
        "highscore_filename": "highscore.json",
        "lives": 3,
        "points_per_pacgum": 10,
        "points_per_super_pacgum": 50,
        "points_per_ghost": 200,
        "seed": 42,
        "level_max_time": 90,
    }

    def __init__(self,
                 highscore_filename: str = default["highscore_filename"],
                 lives: int = default["lives"],
                 points_per_pacgum: int = default["points_per_pacgum"],
                 points_per_super_pacgum: int = (
                     default["points_per_super_pacgum"]),
                 points_per_ghost: int = default["points_per_ghost"],
                 seed: int = default["seed"],
                 level_max_time: int = default["level_max_time"]) -> None:
        self.config_file_errors: list[str] = []

        self._set_highscore_filename(highscore_filename)
        self._set_lives(lives)
        self._set_points_per_pacgum(points_per_pacgum)
        self._set_points_per_super_pacgum(points_per_super_pacgum)
        self._set_points_per_ghost(points_per_ghost)
        self._set_seed(seed)
        self._set_level_max_time(level_max_time)

    def _set_highscore_filename(self, highscore_filename: str) -> None:
        error_msg = "highscore_filename"
        if not isinstance(highscore_filename, str):
            error_msg += " must be a string"
        elif len(highscore_filename) == 0:
            error_msg += " must contain characters"
        elif not highscore_filename.endswith(".json"):
            error_msg += " must be a JSON file"
        else:
            self.highscore_filename: str = highscore_filename
            return

        self.highscore_filename = self.default["highscore_filename"]
        self.config_file_errors.append(error_msg)

    def _set_lives(self, lives: int) -> None:
        error_msg = "lives"
        if not isinstance(lives, int):
            error_msg += " must be an int"
        elif lives < 1:
            error_msg += " must be > 0"
        else:
            self.lives: int = lives
            return

        self.lives = self.default["lives"]
        self.config_file_errors.append(error_msg)

    def _set_points_per_pacgum(self, points_per_pacgum: int) -> None:
        error_msg = "points_per_pacgum"
        if not isinstance(points_per_pacgum, int):
            error_msg += " must be an int"
        elif points_per_pacgum < 1:
            error_msg += " must be > 0"
        else:
            self.points_per_pacgum: int = points_per_pacgum
            return

        self.points_per_pacgum = self.default["points_per_pacgum"]
        self.config_file_errors.append(error_msg)

    def _set_points_per_super_pacgum(self,
                                     points_per_super_pacgum: int) -> None:
        error_msg = "points_per_super_pacgum"
        if not isinstance(points_per_super_pacgum, int):
            error_msg += " must be an int"
        elif points_per_super_pacgum < 1:
            error_msg += " must be > 0"
        else:
            self.points_per_super_pacgum: int = points_per_super_pacgum
            return

        self.points_per_super_pacgum = (
            self.default["points_per_super_pacgum"]
        )
        self.config_file_errors.append(error_msg)

    def _set_points_per_ghost(self, points_per_ghost: int) -> None:
        error_msg = "points_per_ghost"
        if not isinstance(points_per_ghost, int):
            error_msg += " must be an int"
        elif points_per_ghost < 1:
            error_msg += " must be > 0"
        else:
            self.points_per_ghost: int = points_per_ghost
            return

        self.points_per_ghost = self.default["points_per_ghost"]
        self.config_file_errors.append(error_msg)

    def _set_seed(self, seed: int) -> None:
        error_msg = "seed"
        if not isinstance(seed, int):
            error_msg += " must be an int"
        else:
            self.seed: int = seed
            return

        self.seed = self.default["seed"]
        self.config_file_errors.append(error_msg)

    def _set_level_max_time(self, level_max_time: int) -> None:
        error_msg = "level_max_time"
        if not isinstance(level_max_time, int):
            error_msg += " must be an int"
        elif level_max_time < 60:
            error_msg += " must be >= 60"
        else:
            self.level_max_time: int = level_max_time
            return

        self.level_max_time = self.default["level_max_time"]
        self.config_file_errors.append(error_msg)


def _strip_comments(text: str) -> str:
    lines = [line for line in text.splitlines()
             if not line.lstrip().startswith("#")]
    return "\n".join(lines)


def load_config(path: str) -> Config:
    try:
        with open(path) as f:
            text = f.read()
    except OSError as e:
        raise ConfigError(f"Could not open '{path}': {e.strerror}")
    except UnicodeDecodeError:
        raise ConfigError(f"Could not open '{path}': invalid file type")

    try:
        data = json.loads(_strip_comments(text))
    except json.JSONDecodeError as e:
        raise ConfigError(f"Bad JSON format in '{path}':"
                          f" {e.msg} (line {e.lineno}, column {e.colno})")
    if not isinstance(data, dict):
        raise ConfigError(f"Bad format in '{path}': data must be"
                          " represented in an object")

    for key in data:
        if key not in Config.default:
            print(f"[WARNING] {path}: unknown key '{key}' ignored")
    for key in Config.default:
        if key not in data:
            print(f"[WARNING] {path}: missing key '{key}',"
                  f" using default value {Config.default[key]!r}")

    known = {key: value for key, value in data.items()
             if key in Config.default}
    config = Config(**known)
    for error in config.config_file_errors:
        print(f"[WARNING] {path}: {error}, using default value")
    return config
