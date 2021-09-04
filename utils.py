import re
import os
import sys


def title_case(s: str) -> str:
    # fix with regex stuff I guess
    return (
        re.sub(r"([0-9][A-Z][a-z])", r"\1".lower(), s.title())
        .replace("'S", "'s")
        .replace("Ii", "II")
        .replace("'T", "'t")
    )


def get_path_to_resource(filename: str, foldername: str = "translations"):
    dirname: str = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(dirname, foldername, filename)
