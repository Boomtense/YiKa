import re


def title_case(s: str) -> str:
    # fix with regex stuff I guess
    return (
        re.sub(r"([0-9][A-Z][a-z])", r"\1".lower(), s.title())
        .replace("'S", "'s")
        .replace("Ii", "II")
        .replace("'T", "'t")
    )
