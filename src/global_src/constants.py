from pathlib import Path

ROOT_FOLDER = Path(__file__).parent.parent.parent

SRC_FOLDER = ROOT_FOLDER / "src"
FILES_FOLDER = ROOT_FOLDER / "_files"

CORE_FOLDER = SRC_FOLDER / "core"
DATABASE_FOLDER = SRC_FOLDER / "database"
GLOBAL_SRC_FOLDER = SRC_FOLDER / "global_src"

DATABASE_PATH = DATABASE_FOLDER / "pesignup.db"


if __name__ == "__main__":
    print(f"Root folder: {ROOT_FOLDER}")
