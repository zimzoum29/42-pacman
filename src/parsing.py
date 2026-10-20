from pydantic import BaseModel, Field, ValidationError
from typing import TextIO
from pathlib import Path
import json
import os
import re

HIGHSCORES_DIR = Path(__file__).resolve().parents[1] / "highscores"
MAX_PLAYERS = 10
NAME_PATTERN = re.compile(r"[A-Za-z0-9 ]{1,10}")


class Config(BaseModel):

    highscore_filename: str = Field(min_length=1)
    lives: int = Field(ge=1)
    points_per_pacgum: int = Field(ge=1)
    points_per_super_pacgum: int = Field(ge=1)
    points_per_ghost: int = Field(ge=1)
    seed: int
    level_max_time: int = Field(ge=60, default=90)


class FileInterface:

    def __init__(self, config_file: str) -> None:

        actual_file: str = str(Path(config_file).resolve())
        try:
            with open(config_file) as f:
                self.config: Config = self.get_config(f)
            self._highscores_path: Path = (
                HIGHSCORES_DIR / Path(self.config.highscore_filename).name
            )
            self.highscores: dict[str, int] = self.get_highscores()

        except ValidationError as e:
            error_msg = "[ERROR] Bad format in configuration file:"
            for error in e.errors():
                error_msg += f"\n - {error["loc"][0]}: {error["msg"]}"
            raise ValueError(error_msg)
        except json.JSONDecodeError as e:
            raise ValueError(f"[ERROR] Bad json format in '{actual_file}'."
                             f" {str(e).split(" (char ")[0]}")
        except UnicodeDecodeError:
            raise ValueError(f"[ERROR] Could not open '{actual_file}':"
                             " Invalid file type")
        except ValueError as e:
            raise ValueError("[ERROR] " + str(e))
        except OSError as e:
            if e.filename:
                raise OSError(f"[ERROR] Could not open '{actual_file}':"
                              f" {e.strerror}")
            else:
                raise OSError(f"{e} ({type(e).__name__})")

    def get_config(self, config_file: TextIO) -> Config:

        json_file: str = ""
        for line in config_file:
            line = line.split('#')[0].rstrip() + '\n'
            if line:
                json_file += line

        config = json.loads(json_file)
        if not isinstance(config, dict):
            raise ValueError("Bad format in configuration file, data must be"
                             " represented in an object")

        return Config(**config)
    @staticmethod
    def is_valid_entry(player: object, score: object) -> bool:
        return (isinstance(player, str)
                and NAME_PATTERN.fullmatch(player) is not None
                and isinstance(score, int)
                and not isinstance(score, bool)
                and score >= 0)

    @staticmethod
    def _top(highscores: dict[str, int]) -> dict[str, int]:
        ranking = sorted(highscores.items(),
                         key=lambda item: item[1], reverse=True)
        return dict(ranking[:MAX_PLAYERS])

    def get_highscores(self) -> dict[str, int]:
        path = self._highscores_path
        try:
            with open(path) as f:
                data = json.load(f)
        except FileNotFoundError:
            return {}
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
            print(f"[WARNING] Cannot read '{path}' ({e}),"
                  " starting with an empty leaderboard")
            return {}

        if not isinstance(data, dict):
            print(f"[WARNING] '{path}' must contain a JSON object,"
                  " starting with an empty leaderboard")
            return {}

        highscores: dict[str, int] = {}
        for player, score in data.items():
            if not self.is_valid_entry(player, score):
                print(f"[WARNING] Ignoring invalid highscore entry"
                      f" {player!r}: {score!r}")
                continue
            highscores[player] = score
        return self._top(highscores)

    def update_highscores(self, player: str, score: int) -> dict[str, int]:
        if not self.is_valid_entry(player, score):
            print(f"[WARNING] Invalid highscore {player!r}: {score!r}")
            return self.highscores
        if score <= self.highscores.get(player, -1):
            return self.highscores
        self.highscores[player] = score
        self.highscores = self._top(self.highscores)
        self.save_highscores()
        return self.highscores

    def save_highscores(self) -> None:
        path = self._highscores_path
        tmp = path.with_name(path.name + ".tmp")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(tmp, "w") as f:
                json.dump(self.highscores, f, indent=4)
            os.replace(tmp, path)
        except OSError as e:
            print(f"[WARNING] Could not save highscores to '{path}':"
                  f" {e.strerror}")

if __name__ == "__main__":
    try:
        parser = FileInterface("test.json")
    except Exception as e:
        print(e)
        exit()
    print(parser.config)
    print(parser.highscores)
