import os
import sys
from functools import wraps


class StdoutNull:
    """
    This class is a context manager used to redirect stdout to /dev/null
    """

    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


def block_stdout(func):
    """
    This decorator blocks stdout for the wrapped function
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        with StdoutNull():
            func(*args, **kwargs)

    return wrapper


def generate_path_completions(path):
    """
    This generates a list of paths for dash dropdown options
    """
    path_completions = []
    home_dir = os.path.expanduser("~")
    abs_path = os.path.join(home_dir, path)
    if os.path.isdir(abs_path):
        files_and_dirs = os.listdir(abs_path)
        files_and_dirs_no_hidden = [f for f in files_and_dirs if not f.startswith(".")]
        for item in files_and_dirs_no_hidden:
            item_path = os.path.join(path, item)
            abs_item_path = os.path.join(home_dir, item_path)
            if os.path.isdir(abs_item_path):
                path_completions.append({"label": item + "/", "value": item_path + "/"})
            else:
                path_completions.append({"label": item, "value": item_path})
    return path_completions
