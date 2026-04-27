import os
from pathlib import Path

ROOT_FOLDER = Path(__file__).parent.parent.parent

SRC_FOLDER = ROOT_FOLDER / "src"
FILES_FOLDER = ROOT_FOLDER / "_files"

CORE_FOLDER = SRC_FOLDER / "core"
DATABASE_FOLDER = CORE_FOLDER / "database"
GLOBAL_SRC_FOLDER = CORE_FOLDER / "global_src"


if __name__ == "__main__":
    print(f"Root folder: {ROOT_FOLDER}")
