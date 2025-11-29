#! /usr/bin/python

import asyncio
import re
import pandas as pd
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import NetworkError

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore

from dotenv import load_dotenv
from os import chdir, getenv
from pathlib import Path
import sys

from utils.funcs import log_print
from utils.commands import help, gabbia, bossetti, schedule, todo, venerdi
from utils.const import TRIGGERS,DEMONIMI

#: Messaggio manuale da shell Bash
#: curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" -d "chat_id=<GROUP_ID>&text=CIMMIA 🦧"

if sys.argv[0] != Path(__file__).name:
    chdir(Path(__file__).parent)

CWD = Path.cwd()


load_dotenv(CWD / '.env')
TOKEN    = getenv('TOKEN', '')  
GROUP_ID = int(getenv('GROUP_ID', ''))
BOSSETTI = getenv('BOSSETTI', '')
TO_DO    = getenv('TO_DO', '')

triggers: pd.DataFrame = pd.concat([pd.read_csv(TRIGGERS), pd.read_csv(DEMONIMI)], axis=0, ignore_index=True)

scheduler = BackgroundScheduler()

SILENT = 'silent' in sys.argv

async def send_startup_message(bot: Bot):
    from utils.const import startup_msg
    STARTUP_MSG = startup_msg()
    await bot.send_message(chat_id=GROUP_ID, text=STARTUP_MSG, parse_mode=ParseMode.MARKDOWN)

async def send_shutdown_message(bot: Bot):
    from utils.const import shutdown_msg
    SHUTDOWN_MSG = shutdown_msg()
    await bot.send_message(chat_id=GROUP_ID, text=SHUTDOWN_MSG, parse_mode=ParseMode.MARKDOWN)

# /help
async def slash_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = help(Path(__file__), context.args)
        await update.message.reply_text(text=text)#, parse_mode=ParseMode.MARKDOWN_V2) # type: ignore
    except (KeyError, FileNotFoundError) as e:
        await update.message.reply_text( # type: ignore
            f"CRY! - {type(e).__name__}: {e}\nUso corretto:\n"
            "/help: Mostra elenco dei comandi disponibili"
        )

# /gabbia <minuti>
async def slash_gabbia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        in_cage, seconds, out_cage = gabbia(context.args)
        await update.message.reply_text(in_cage) # type: ignore
        await asyncio.sleep(seconds)
        await update.message.reply_text(out_cage) # type: ignore
    except (KeyError, ValueError) as e:
        await update.message.reply_text( # type: ignore
            f"CRY! - {type(e).__name__}: {e}\nUso corretto:\n"
            "/gabbia <minuti>"
        )

# /bossetti <show>
async def slash_bossetti(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = CWD / BOSSETTI
    try:
        msg = bossetti(path, context.args)
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2) # type: ignore
    except KeyError as e:
        await update.message.reply_text( # type: ignore
            f"CRY! - {type(e).__name__}: {e}\nUso corretto:\n"
            "/bossetti: Aumenta silentemente il contatore;\n"
            "/bossetti show: Mostra il valore attuale del contatore."
        )

# Invio messaggio programmato, con data e ora di schedulazione
async def scheduled_message(context: ContextTypes.DEFAULT_TYPE, msg: str, dt: str):
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text='{0}\n(Questo messaggio fu programmato in data {1} alle ore {2})'.format(
            msg, *dt.split(' ')
        )
    )

# /schedule m 10 Questo messaggio arriva tra 10 minuti
async def slash_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        text, scheduled_on, scheduled_for = schedule(context.args)

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
    todo_md = (CWD / TO_DO)
    try:
        msg = todo(todo_md, context.args)
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN_V2)  # type: ignore
    except KeyError as e:
        await update.message.reply_text( # type: ignore
            f"CRY! - {type(e).__name__}: {e}\nUso corretto:\n"
            "/todo: Elenca le features da implementare;\n"
            "/todo add testo: Aggiunge testo alla To-Do list."
        )

async def slash_venerdi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = venerdi(context.args)
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)  # type: ignore
    except KeyError as e:
        await update.message.reply_text( # type: ignore
            f"CRY! - {type(e).__name__}: {e}\nUso corretto:\n"
            "/venerdi: Seleziona un pub casuale in cui andare."
        )

# Trigger
async def reply_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    if update.message and update.message.text:
        text = update.message.text.lower()
        words = triggers['trigger'].tolist()
        triggereds = re.findall('|'.join(words), text)
        if triggereds:
            reply = triggers.set_index('trigger').loc[triggereds]['risposta'].values
            if len(reply) == 1:
                msg = reply[0]
            else:
                msg = f'Ho {len(reply)} osservazioni da fare:\n' + '\n'.join(f'{i}. {txt.replace("\n", " ")}' for i, txt in enumerate(reply, start=1))
            await update.message.reply_text(msg)

async def error_handler(update, context):
    if context.error:
        try:
            raise context.error
        except NetworkError as e:
            log_print('WARNING', f"Network error: {e}, retrying...")
            await asyncio.sleep(5)
        except Exception as e:
            log_print('ERROR', f"Unhandled exception: {type(e).__name__}: {e}")

# Avvio bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    # per mandare messaggi al di fuori da asyncio
    bot = Bot(token=TOKEN)

    # Scheduler background
    scheduler.start()

    # Comandi
    # app.add_handler(CommandHandler("start", slash_start))
    app.add_handler(CommandHandler("help", slash_help))
    app.add_handler(CommandHandler("schedule", slash_schedule))
    app.add_handler(CommandHandler("todo", slash_todo))
    app.add_handler(CommandHandler("gabbia", slash_gabbia))
    app.add_handler(CommandHandler("bossetti", slash_bossetti))
    app.add_handler(CommandHandler("venerdi", slash_venerdi))

    # Trigger
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_trigger))

    # Error Handling
    app.add_error_handler(error_handler)

    # Funzioni di startup/shutdown automatiche
    async def on_startup(app):
        await send_startup_message(bot)
        log_print('INFO', "✅ [STARTUP] Messaggio inviato al gruppo")

    async def on_shutdown(app):
        await send_shutdown_message(bot)
        log_print('INFO', "✅ Messaggio di chiusura inviato")
        scheduler.shutdown(wait=False)
        log_print('INFO', "✅ Scheduler chiuso correttamente")

    log_print('INFO', "✅ WelbyBot attivo! " + "Premi Ctrl+C per uscire.\n".upper())

    # Registra i callback
    if not SILENT:
        app.post_init = on_startup
        app.post_shutdown = on_shutdown
    else:
        log_print('INFO', "\t\t-- Modalità Silenziosa --".upper())
        log_print('INFO', "\t\t-- ANoDoRea non si presenterà al suo ingresso in chat -- \n")

    try:
        app.run_polling()
    except KeyboardInterrupt:
        log_print('EXIT', "Interruzione manuale (Ctrl+C).")
    except Exception as e:
        log_print('CRITICAL', f"{type(e).__name__}: {e}")
    finally:
        log_print('INFO', "✅ WelbyBot terminato correttamente.")


if __name__ == "__main__":
    main()
