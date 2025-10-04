#! /usr/bin/python

import asyncio
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import NetworkError

from apscheduler.schedulers.background import BackgroundScheduler # type: ignore

from datetime import datetime, timedelta
import re

from dotenv import load_dotenv
import os
import sys


#: Messaggio manuale da shell Bash
#: curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" -d "chat_id=<GROUP_ID>&text=CIMMIA 🦧"


load_dotenv(os.path.join(os.getcwd(), '.env'))
TOKEN = os.getenv('TOKEN', '')  
GROUP_ID = int(os.getenv('GROUP_ID', ''))

scheduler = BackgroundScheduler()

SILENT = 'silent' in sys.argv

async def send_startup_message(bot: Bot):
    GITHUB_PAGE = '[WelbyBot](https://github.com/m-contini/WelbyBot)'

    # Legge versione e data release da README
    with open(os.path.join(os.getcwd(), 'README.md'), 'r', encoding='utf-8', errors='ignore') as README:
        match = re.search(r"Versione:.+?(\d*\.\d*).+?Data rilascio:.+?(\d+-\d+-\d+)", README.read(), re.DOTALL)
        if match:
            VERSION, RELEASED = match.groups()

    text = (
        "🤖 *WelbyBot* - *Online*. *Me ne frego!*",
        f"(Ultima _scopata_: {ita_string(datetime.now())})",
        f"Incontrami: {GITHUB_PAGE}",
        f"v{VERSION} ({RELEASED})"
    )
    await bot.send_message(chat_id=GROUP_ID, text='\n'.join(text), parse_mode=ParseMode.MARKDOWN)

async def send_shutdown_message(bot: Bot):
    text = (
        "🤖 *WelbyBot* - *Offline*.",
        "Alla prossima (ah che) _scopata_!"
    )
    await bot.send_message(chat_id=GROUP_ID, text='\n'.join(text), parse_mode=ParseMode.MARKDOWN)

def ita_string(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y %H:%M:%S")

# /gabbia <minuti>
async def slash_gabbia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args or len(context.args) != 1:
            raise KeyError
        minutes = float(context.args[0])
        if minutes <= 0:
            raise ValueError
        until = datetime.now() + timedelta(minutes=minutes)
        await update.message.reply_text(f"Ok, vado in gabbia fino a: {ita_string(until)}.\nSi spera si scopi. Esperémos que escopamos; nucha chupar el chorrizo.") # type: ignore
        await asyncio.sleep(minutes * 60)
        await update.message.reply_text("Sono uscito dalla gabbia, che scopata che mi son fatto!") # type: ignore
    except (KeyError, ValueError) as e:
        await update.message.reply_text( # type: ignore
            f"CRY! - {type(e).__name__}: {e}\nUso corretto:\n"
            "/gabbia <minuti>"
        )

# /bossetti
async def slash_bossetti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            if context.args[0].lower() != 'show':
                raise KeyError
            with open('autism_log.csv', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            datestr, counterstr = lines[-1].strip().split(';')
            date: str = ita_string(datetime.strptime(datestr, '%Y-%m-%d %H:%M:%S.%f'))
            counterstr = f'{counterstr:,}'.replace(',', '.')
            await update.message.reply_text(f"Autism attuale: {counterstr}, incrementato il {date}") # type: ignore
        except FileNotFoundError:
            await update.message.reply_text("Autism attuale: 0") # type: ignore
        except KeyError as e:
            await update.message.reply_text( # type: ignore
                f"CRY! - {type(e).__name__}: {e}\nUso corretto:\n"
                "/bossetti: aumenta silentemente il contatore;\n"
                "/bossetti show: mostra il valore attuale del contatore."
            )
    else:
        try:
            with open('autism_log.csv', 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            with open('autism_log.csv', 'w', encoding='utf-8') as f:
                f.write('Timestamp;AutismCounter\n')
            lines = []

        counter = 0 if not lines else int(lines[-1].split(';')[-1].strip())
        now = datetime.now()

        counter += 1
        with open('autism_log.csv', 'a', encoding='utf-8') as f:
            f.write(f'{now};{counter}\n')

# /start
async def slash_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Il mio nome: Welby\nIl mio scopo: rubarti la Bocca.")

# Invio messaggio programmato, con data e ora di schedulazione
async def scheduled_message(context: ContextTypes.DEFAULT_TYPE, text: str, dt: datetime):
    date, time = ita_string(dt).split()
    msg = text + f'\n(Questo messaggio fu programmato in data {date} alle ore {time})'
    await context.bot.send_message(chat_id=GROUP_ID, text=msg)

# /schedule m 10 Questo messaggio arriva tra 10 minuti
async def slash_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        if not context.args or len(context.args) < 3:
            raise KeyError

        unit, value = context.args[0], float(context.args[1])
        text = " ".join(context.args[2:])

        scheduled_on = datetime.now()
        conversion = dict(s=1, m=60, h=3600, d=3600*24)[unit]
        scheduled_for = scheduled_on + timedelta(seconds=value*conversion)

        # Salva loop principale (quello del bot)
        loop = asyncio.get_running_loop()

        # Funzione che esegue la coroutine sul loop principale
        def job():
            asyncio.run_coroutine_threadsafe(
                scheduled_message(context, text, scheduled_on),
                loop
            )

        scheduler.add_job(job, trigger='date', run_date=scheduled_for)

        await update.message.reply_text(f"Sugi pula nel frattempo ☀️.") # type: ignore

    except (KeyError, ValueError) as e:
        await update.message.reply_text( # type: ignore
            f"CRY! - {type(e).__name__}: {e}\nUso corretto:\n"
            "/schedule <unità s|m|h|d> <valore> <messaggio>"
        )

# /todo "add", "Feature", "da", "implementare"
async def slash_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    def escape_markdown_v2(text: str) -> str:
        # Escapa tutti i caratteri speciali Markdown V2
        return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

    if context.args:
        try:
            if context.args[0] != 'add' or len(context.args) <= 1:
                raise KeyError
            with open(os.path.join(os.getcwd(), 'ToDo.md'), 'a', encoding='utf-8', errors='ignore') as TODO:
                TODO.write('- ' + ' '.join(context.args[1:]) + ';  \n')
            await update.message.reply_text("✅ Nuova voce aggiunta!")  # type: ignore
            return
        except KeyError as e:
            await update.message.reply_text( # type: ignore
                f"CRY! - {type(e).__name__}: {e}\nUso corretto:\n"
                "/todo: Elenca le features da implementare;\n"
                "/todo add implementa_un_contatore_autistico: Aggiunge riga alla To-Do list)"
            )
    else:
        i = 0
        todos = []
        with open(os.path.join(os.getcwd(), 'ToDo.md'), 'r', encoding='utf-8', errors='ignore') as TODO:
            for line in TODO:
                match = re.search(r"- (.+)$", line)
                if not match:
                    continue
                i += 1
                line = rf'{i}. {match.group(1).strip()}'
                todos.append(escape_markdown_v2(line))
        if todos:
            await update.message.reply_text(text='\n'.join(todos), parse_mode=ParseMode.MARKDOWN_V2) # type: ignore
        else:
            await update.message.reply_text("Nessuna voce trovata") # type: ignore

# Trigger
async def trigger_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        text = update.message.text.lower()
        reply = []
        if "negr" in text:
            reply.append("Negri di merda fuori di qua subito 🌻")
        if "palle" in text:
            reply.append("Ah come dici? Ti piacciono i ppall mmocc?!")
        if "sindaco" in text:
            reply.append("Oh sì Sindaco ingoia tutto Sindaco.")
        if "uccell" in text:
            reply.append("Uccellino di merda se ti becco ti ammazzo.")
        if "chorizo" in text:
            reply.append("Oh sì chorizo. Siempre chupando el chorizo, finocchio del cazzo.")
        if "frocio" in text:
            reply.append("Come combatto un frocio?\nScopandolo io prima che lui scopi me.\nSe io non scopo lui, infatti, lui scoperà me.")

        if len(reply) == 1:
            await update.message.reply_text(reply[0])
        elif len(reply) > 1:
            await update.message.reply_text(f'Ho {len(reply)} osservazioni da fare:\n' + '\n'.join(f'{i}. {txt.replace('\n', ' ')}' for i, txt in enumerate(reply, start=1)))

async def error_handler(update, context):
    try:
        when = ita_string(datetime.now())
        if context.error:
            raise context.error
    except NetworkError as e:
        print(f"[WARN] {when} Network error: {e}, retrying...")
        await asyncio.sleep(5)
    except Exception as e:
        print(f"[ERROR] {when} Unhandled exception: {type(e).__name__}: {e}")

# Avvio bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    # per mandare messaggi al di fuori da asyncio
    bot = Bot(token=TOKEN)

    # Scheduler background
    scheduler.start()

    # Comandi
    app.add_handler(CommandHandler("start", slash_start))
    app.add_handler(CommandHandler("schedule", slash_schedule))
    app.add_handler(CommandHandler("todo", slash_todo))
    app.add_handler(CommandHandler("gabbia", slash_gabbia))
    app.add_handler(CommandHandler("bossetti", slash_bossetti))

    # Trigger
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, trigger_reply))

    # Error Handling
    app.add_error_handler(error_handler)

    # Funzioni di startup/shutdown automatiche
    async def on_startup(app):
        await send_startup_message(bot)
        print("\n✅ [STARTUP] Messaggio inviato al gruppo")

    async def on_shutdown(app):
        await send_shutdown_message(bot)
        print("\n✅ Messaggio di chiusura inviato")
        scheduler.shutdown(wait=False)
        print("\n✅ Scheduler chiuso correttamente")

    print("\n\t✅ WelbyBot attivo!" + "Premi Ctrl+C per uscire.\n".upper())

    # Registra i callback
    if not SILENT:
        app.post_init = on_startup
        app.post_shutdown = on_shutdown
    else:
        print("\t\t-- Modalità Silenziosa --".upper(), "\t\t-- ANoDoRea non si presenterà al suo ingresso in chat -- \n", sep='\n')

    try:
        app.run_polling()
    except KeyboardInterrupt:
        when = ita_string(datetime.now())
        print(f"[EXIT] {when} Interruzione manuale (Ctrl+C).")
    except Exception as e:
        when = ita_string(datetime.now())
        print(f"[CRITICAL] {when} {type(e).__name__}: {e}")
    finally:
        print("[EXIT] WelbyBot terminato correttamente.")


if __name__ == "__main__":
    main()
