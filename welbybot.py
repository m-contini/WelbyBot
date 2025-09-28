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

async def send_startup_message(bot: Bot):
    GITHUB_PAGE = '[WelbyBot](https://github.com/m-contini/WelbyBot)'

    # Legge versione e data release da README
    with open(os.path.join(os.getcwd(), 'README.md'), 'r', encoding='utf-8', errors='ignore') as README:
        match = re.search(r"Versione:.+?(\d*\.\d*).+?Data rilascio:.+?(\d+-\d+-\d+)", README.read(), re.DOTALL)
        if match:
            VERSION, RELEASED  = match.groups()

    text = (
        "🤖 *WelbyBot* - *Online*. *Me ne frego!*",
        f"(Ultima _scopata_: {ita_string(datetime.now())})",
        f"Incontrami: {GITHUB_PAGE}",
        f"v{VERSION} ({RELEASED})"
    )
    await bot.send_message(chat_id=GROUP_ID, text='\n'.join(text), parse_mode=ParseMode.MARKDOWN)

async def send_shutdown_message(bot: Bot):
    text = (
        "🤖 *WelbyBot* - *Offline*."
        "Alla prossima (ah che) _scopata_!"
    )
    await bot.send_message(chat_id=GROUP_ID, text=text, parse_mode=ParseMode.MARKDOWN)

def ita_string(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y %H:%M:%S")

# /start
async def slash_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Il mio nome: Welby\nIl mio scopo: rubarti la Bocca.")

# Invio messaggio programmato, con data e ora di schedulazione
async def scheduled_message(context: ContextTypes.DEFAULT_TYPE, text: str, dt: datetime):
    date, time = ita_string(dt).split()
    msg = text + f'\n(Questo messaggio fu programmato in data {date} alle ore {time})'
    await context.bot.send_message(chat_id=GROUP_ID, text=msg)

# /schedule
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
        await update.message.reply_text(f"CRY! - {type(e).__name__}: {e}\nUso corretto: /schedule <unità s|m|h|d> <valore> <messaggio>") # type: ignore

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
        if "frocio" in text:
            reply.append("Come combatto un frocio?\nScopandolo io prima che lui scopi me.\nSe io non scopo lui, infatti, lui scoperà me.")

        if len(reply) == 1:
            await update.message.reply_text(reply[0])
        elif len(reply) > 1:
            await update.message.reply_text(f'Ho {len(reply)} osservazioni da fare:\n' + '\n'.join(f'{i}. {txt.replace('\n', ' ')}' for i, txt in enumerate(reply, start=1)))

async def error_handler(update, context):
    try:
        raise context.error
    except NetworkError as e:
        print(f"[WARN] Network error: {e}, retrying...")
        await asyncio.sleep(5)
    except Exception as e:
        print(f"[ERROR] Unhandled exception: {type(e).__name__}: {e}")

# Avvio bot
# async def main():
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    # per mandare messaggi al di fuori da asyncio
    bot = Bot(token=TOKEN)

    # Scheduler background
    scheduler.start()

    # Comandi
    app.add_handler(CommandHandler("start", slash_start))
    app.add_handler(CommandHandler("schedule", slash_schedule))


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

    # Registra i callback
    app.post_init = on_startup
    app.post_shutdown = on_shutdown

    print("\n\t✅ WelbyBot attivo!" + "Premi Ctrl+C per uscire.\n".upper())

    try:
        app.run_polling()
    except KeyboardInterrupt:
        print("[EXIT] Interruzione manuale (Ctrl+C).")
    except Exception as e:
        print(f"[CRITICAL] {type(e).__name__}: {e}")
    finally:
        print("[EXIT] WelbyBot terminato correttamente.")


if __name__ == "__main__":
    main()
