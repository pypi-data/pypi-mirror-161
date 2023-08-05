"""Input / output functionality."""
import json
from typing import List, Any

from schiller.fs_util import PathLike, _add_ext


def save_txt_lines(f_path: PathLike, s_list: List[str]) -> None:
    """Saves a list of strings to a text file.

    Args:
        f_path: Path of file to be written.
        s_list: List with strings containing the lines.
    """
    with open(f_path, "w") as f:
        f.write("\n".join(s_list))


def read_txt_lines(f_path: PathLike) -> List[str]:
    """Reads a text file and returns the lines.

    Args:
        f_path: Path to file to be read.
    """
    with open(f_path, "r") as f:
        return f.read().splitlines()


def write_json(f_path: PathLike, data: Any) -> None:
    """Saves the data to a json file.

    Args:
        f_path: Path of file to be written.
        data: Json serializable data.
    """
    f_path_str = _add_ext(f_path, ".json")
    with open(f_path_str, "w") as outfile:
        json.dump(data, outfile, indent="    ")


def read_json(f_path: PathLike) -> Any:
    """Reads a json file.

    Args:
        f_path: Path to file to be read.
    """
    f_path_str = _add_ext(f_path, ".json")
    with open(f_path_str, "r") as f:
        return json.loads(f.read())


# Aliases
save_json = write_json  #: Alias to write_json
write_txt_lines = save_txt_lines  #: Alias to write_json
