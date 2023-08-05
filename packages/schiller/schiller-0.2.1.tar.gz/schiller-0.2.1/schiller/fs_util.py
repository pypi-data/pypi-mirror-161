"""File system utility."""
import os
from pathlib import Path
from typing import Union

PathLike = Union[str, bytes, os.PathLike]  #: Path-like object type


def _add_ext(f_name: PathLike, ext: str) -> str:
    if isinstance(f_name, bytes):
        f_name_str = f_name.decode()
    else:
        f_name_str = str(f_name)

    if not f_name_str.endswith(ext):
        f_name_str = f"{f_name_str}{ext}"
    return f_name_str


def to_path(path: PathLike) -> Path:
    """Converts a PathLike path to a Path.

    Args:
        path: Path-like object.
    """
    if isinstance(path, bytes):
        path = path.decode()
    return Path(path)


def create_dir(d_name: PathLike) -> None:
    """Creates a directory if it does not yet exist.

    Also creates its parents if they do not yet exist.

    Args:
        d_name: Path to the directory to create.
    """
    d_name_path = to_path(d_name)
    if not d_name_path.is_dir():
        d_name_path.mkdir(exist_ok=True, parents=True)
