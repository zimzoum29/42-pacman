import json
import os
import re
from pathlib import Path

MAX_PLAYERS = 10
NAME_PATTERN = re.compile(r"[A-Za-z0-9 ]{1,10}")


class Highscores:

    def __init__(self, path: Path) -> None:
        self._path = path
        self.scores: dict[str, int] = self._load()

    @staticmethod
    def is_valid_entry(player: object, score: object) -> bool:
        return (isinstance(player, str)
                and NAME_PATTERN.fullmatch(player) is not None
                and isinstance(score, int)
                and not isinstance(score, bool)
                and score >= 0)

    @staticmethod
    def _top(scores: dict[str, int]) -> dict[str, int]:
        ranking = sorted(scores.items(),
                         key=lambda item: item[1], reverse=True)
        return dict(ranking[:MAX_PLAYERS])

    def _load(self) -> dict[str, int]:
        path = self._path
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

        scores: dict[str, int] = {}
        for player, score in data.items():
            if not self.is_valid_entry(player, score):
                print(f"[WARNING] Ignoring invalid highscore entry"
                      f" {player!r}: {score!r}")
                continue
            scores[player] = score
        return self._top(scores)

    def update(self, player: str, score: int) -> dict[str, int]:
        if not self.is_valid_entry(player, score):
            print(f"[WARNING] Invalid highscore {player!r}: {score!r}")
            return self.scores
        if score <= self.scores.get(player, -1):
            return self.scores
        self.scores[player] = score
        self.scores = self._top(self.scores)
        self.save()
        return self.scores

    def save(self) -> None:
        path = self._path
        tmp = path.with_name(path.name + ".tmp")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(tmp, "w") as f:
                json.dump(self.scores, f, indent=4)
            os.replace(tmp, path)
        except OSError as e:
            print(f"[WARNING] Could not save highscores to '{path}':"
                  f" {e.strerror}")
