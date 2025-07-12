import platform
from pathlib import Path

from vebp.Libs.File.path import MPath_


def get_venv_python(venv: str = ".venv"):
    venv_dir = MPath_.cwd / Path(venv)

    if not venv_dir.exists():
        return None

    if platform.system() == "Windows":
        python_path = venv_dir / "Scripts" / "python.exe"
    else:
        python_path = venv_dir / "bin" / "python"

    if python_path.exists():
        return python_path
    return "python.exe"