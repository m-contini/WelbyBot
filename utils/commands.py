#! /usr/bin/python

import csv
from datetime import datetime, timedelta
from pathlib import Path
import re
from .funcs import ita_dtime, escape_markdown_v2 # type: ignore

# /help
def _help(path: Path, args) -> str:

    if args:
        raise KeyError("/help non accetta argomenti.")

    code = path.read_text(encoding='utf-8')
    # except FileNotFoundError:
    #     raise FileNotFoundError(f"Impossibile trovare il file 'welbybot.py': {PARENT / 'welbybot.py'}")

    results = {}
    funcs = re.findall(r'async def slash_.+?\s+\)\n', code, re.DOTALL)
    for func in funcs:
        name = re.search(r'slash_(.+?)\(', func)
        if not name:
            continue
        strings = re.findall(r'\"(.+)\n*\"', func)
        if not strings:
            continue
        strings = [s.replace('\\n', '') for s in strings if 'CRY!' not in s]
        results[name.group(1)] = '  \n  '.join(strings)

    items = enumerate(results.items(), start=1)
    return (
        '\n'.join([(f'{i}. {k}:\n  {v}\n') for i, (k, v) in items])
    )

# /gabbia <minuti>
def _gabbia(args) -> tuple[str, float, str]:
    if not args or len(args) != 1:
        raise KeyError
    minutes = float(*args[0])
    if minutes <= 0:
        raise ValueError("Il numero di minuti deve essere positivo.")
    until = datetime.now() + timedelta(minutes=minutes)
    in_cage = (
        f"Ok, vado in gabbia fino a: {ita_dtime(until)}.\n"
        "Si spera si scopi.\n"
        "Esperémos que escopamos; nunca chupar el chorizo."
    )
    seconds: float = minutes * 60
    out_cage = "Sono uscito dalla gabbia, che scopata che mi son fatto!"
    return in_cage, seconds, out_cage

# /bossetti
def _bossetti(path: Path, args) -> str | None:

    mode = 'r' if (args is not None and len(args) > 0) else 'a'
    if args is None:
        args = []
    try:
        if mode == 'r' and args[0].lower() != 'show':
            raise KeyError(args[0]) # type: ignore

        now = datetime.now().replace(microsecond=0)
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';', quotechar="'")
            record: dict = list(reader)[-1]

        date, counter = record.values()
        if mode == 'a':
            with open(path, 'a', encoding='utf-8') as f:
                f.write(f'{now};{int(counter)+1}\n')
            return None

        return (
            "Autism attuale: *{1}*, incrementato il {0}".format(
                ita_dtime(datetime.strptime(date, "%Y-%m-%d %H:%M:%S")),
                f'{int(counter):,}'.replace(',', '.'))
        )
    except FileNotFoundError:
        if mode == 'a':
            with open(path, 'x', encoding='utf-8') as f:
                f.write('Timestamp;AutismCounter\n')
                f.write(f'{now};1\n')
            return None

        return "Autism attuale: 0"

# /schedule
def _schedule(args) -> tuple[str, str, datetime]:

    if not args or len(args) < 3:
        raise KeyError

    unit, value = args[0], float(args[1])
    text = " ".join(args[2:])

    scheduled_on = datetime.now()
    conversion = dict(s=1, m=60, h=3600, d=3600*24)[unit]
    scheduled_for = scheduled_on + timedelta(seconds=value*conversion)
    return text, ita_dtime(scheduled_on), scheduled_for

# /todo
def _todo(path: Path, args) -> str:

    if args:
        if args[0] != 'add' or len(args) <= 1:
            raise KeyError
        append = '- ' + ' '.join(args[1:]) + ';  \n'
        with open(path, 'a', encoding='utf-8', errors='ignore') as todo:
            todo.write(append)
        msg = ("✅ Nuova voce aggiunta!")
    else:
        i = 0
        todos = []
        with open(path, 'r', encoding='utf-8', errors='ignore') as todo:
            for line in todo:
                match = re.search(r"- (.+)$", line)
                if not match:
                    continue
                i += 1
                line = rf'{i}. {match.group(1).strip()}'
                todos.append(line)
        if todos:
            msg = '\n'.join(todos)
        else:
            msg = "Nessuna voce trovata"

    return escape_markdown_v2(msg)
