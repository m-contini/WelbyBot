#! /usr/bin/python

from pathlib import Path
import re
from .funcs import ita_dtime # type: ignore

PARENT = Path(__file__).parent.parent

# Legge versione e data release da README
GITHUB_PAGE = '[WelbyBot](https://github.com/m-contini/WelbyBot)'

def startup_msg() -> str:
    readme_path: Path = PARENT / 'README.md'
    match = re.search(
        r"Versione:.+?(\d*\.\d*).+?Data rilascio:.+?(\d+-\d+-\d+)",
        readme_path.read_text(encoding='utf-8'),
        re.DOTALL
    )
    version, released_on = ('<N/A>', '<N/A>') if not match else match.groups()
    msg = (
            "🤖 *WelbyBot* - *Online*. *Me ne frego!*",
            f"(Ultima _scopata_: {ita_dtime()})",
            f"Incontrami: {GITHUB_PAGE}",
            f"v{version} ({released_on})"
        )
    return '\n'.join(msg)

def shutdown_msg() -> str:
    msg = (
        "🤖 *WelbyBot* - *Offline*.",
        "Alla prossima (ah che) _scopata_!"
    )
    return '\n'.join(msg)

DEMONIMI = PARENT / 'private' / 'demonyms.csv'
TRIGGERS = PARENT / 'private' / 'triggers.csv'