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


class FileInterface:
    """Manage the file interactions"""

    def __init__(self, config_file: str) -> None:
        """Initialize an interface containing the highscores and configuration

        Attributes:
            config_file: The path to the file containing the configuration

        Raises:
            ValueError: If there are problems in an opened file
            OSError: If a file could not be opened
        """

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
            ValueError: If the returned object does not match the
                        needed format.
        """

        highscores_dir = Path(__file__).resolve().parents[1] / "highscores"
        with open(str(highscores_dir / self.config.highscore_filename)) as f:
            highscores = json.loads(f.read())

        if not isinstance(highscores, dict):
            raise ValueError("Bad format in highscores file, data must be"
                             " represented in an object.")
        if len(highscores) > 10:
            raise ValueError("Bad format in highscores file, there must be"
                             " a maximum of 10 players in the highscores file")

        for player in highscores.keys():
            if not isinstance(player, str):
                raise ValueError("Bad format in highscores file, a player's"
                                 " name must be a string")
            import re
            if 1 > len(player) > 10 or not bool(re.fullmatch(r'[A-Za-z0-9 ]+',
                                                             player)):
                raise ValueError("Bad format in highscores file, a player's"
                                 " name must contains between 1 and 10"
                                 " alphanumeric characters")
            if (not isinstance(highscores[player], int)
                    or highscores[player] < -1):
                raise ValueError("Bad format in highscores file, a player's"
                                 " score must be a positive integer")

        return highscores

    def update_highscores(self, player: str, score: int) -> None:
        ...


if __name__ == "__main__":
    try:
        parser = FileInterface("test.json")
    except Exception as e:
        print(e)
        exit()
    print(parser.config)
    print(parser.highscores)
