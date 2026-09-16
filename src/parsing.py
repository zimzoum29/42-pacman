from pydantic import BaseModel, Field, ValidationError
from typing import TextIO
import json
from pathlib import Path


class Config(BaseModel):
    """Represent the informations in the configuration file.

    Attributes:
        highscore_filename: Name of the highscore file, which will be
                            searched in the highcores repository.
        lives: Number of life the player has before game over.
        points_per_pacgum: Number of points earned for "eating" a pacgum.
        points_per_super_pacgum: Number of points earned for "eating"
                                 a super pacgum.
        points_per_ghost: Number of points earned for "eating" a ghost.
        seed: The seed applied to generate the first map.
        level_max_time: The maximum amount of seconds the player has to
                        complete a level.
    """

    highscore_filename: str = Field(min_length=1)
    lives: int = Field(ge=1)
    points_per_pacgum: int = Field(ge=1)
    points_per_super_pacgum: int = Field(ge=1)
    points_per_ghost: int = Field(ge=1)
    seed: int
    level_max_time: int = Field(ge=60, default=90)


class Parser:
    """Parse the configuration and highscores from the input file."""

    def __init__(self, config_file: str) -> None:
        actual_file: str = str(Path(config_file).resolve())
        try:
            with open(config_file) as f:
                self.config: Config = self.get_config(f)
            actual_file = str(Path(__file__).resolve().parents[1]
                              / "highscores" / self.config.highscore_filename)
            self.highscores: dict[str, int] = (
                self.get_highscores()
            )

        except ValidationError as e:
            print(e)
            exit()
        except json.JSONDecodeError as e:
            raise ValueError(f"[ERROR] Bad json format in '{actual_file}'."
                             f" {str(e).split(" (char ")[0]}")
        except UnicodeDecodeError:
            raise ValueError(f"[ERROR] Could not open '{actual_file}':"
                             " Invalid file type")
        except OSError as e:
            if e.filename:
                raise OSError(f"[ERROR] Could not open '{actual_file}':"
                              f" {e.strerror}")
            else:
                raise OSError(f"{e} ({type(e).__name__})")

    def get_config(self, config_file: TextIO) -> Config:
        """Parse the configuration informations.

        Attributes:
            config_file: The opened configuration file.

        Returns:
            A Config object representing the configuration information
            from the input file.

        Raises:
            ValueError: If the extracted type in the json file is not object.
            JSONDecodeError: If the json is badly formatted.
            ValidationError: If configuration datas are invalid/missing.
        """
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

    def get_highscores(self) -> dict[str, int]:
        """Parse the highscores to get the top 10 best players and their score.

        Returns:
            A dict representing the top ten with this format:
            <player>: <score>.

        Raises:
            JSONDecodeError: If the json is badly formatted.
            ValueError: If the extracted type in the json file is not object,
                        a player's name is not a string or if it's score isn't
                        an integer.
        """
        highscores_dir = Path(__file__).resolve().parents[1] / "highscores"
        with open(str(highscores_dir / self.config.highscore_filename)) as f:
            highscores = json.loads(f.read())

        if not isinstance(highscores, dict):
            raise ValueError()

        for player in highscores.keys():
            if not isinstance(player, str):
                raise ValueError()
            if not isinstance(highscores[player], int):
                raise ValueError()

        return highscores


if __name__ == "__main__":
    try:
        parser = Parser("test.json")
    except Exception as e:
        print(e)
        exit()
    print(parser.config)
    print(parser.highscores)
