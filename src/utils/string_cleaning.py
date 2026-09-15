import re


def normalize(name: str) -> str:
    name = re.sub(r"[^\w\s]", "", name)
    return name.lower().strip()