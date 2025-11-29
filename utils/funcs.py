#! /usr/bin/python

from datetime import datetime
import re
from typing import Literal


def ita_dtime(dt: datetime = datetime.now()) -> str:
    return dt.strftime("%d/%m/%Y %H:%M:%S")

def escape_markdown_v2(text: str) -> str:
    # Escapa tutti i caratteri speciali Markdown V2
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

def escape_md2(text: str) -> str:
    special_chars = r"\`[]()~>#+-=|{}.!"
    return re.sub(f"([{re.escape(special_chars)}])", r"\\\1", text)

def log_print(
    type: Literal[
        'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'EXIT'
        ],
    text: str,
    *args,
    **kwargs
) -> None:
    string = f'[{ita_dtime()}] | [{type}] | {text.strip()}'
    if type != 'INFO':
        with open('welbybot.log', 'a+', encoding='utf-8') as log:
            log.write(string + '\n')
    print(string, *args, **kwargs)
