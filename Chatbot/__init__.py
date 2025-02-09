print("[INFO]: INITIALIZING ...")
import re
from time import time
from datetime import datetime
from asyncio import (gather, get_event_loop, sleep)
import requests
from aiohttp import ClientSession
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import (Client, filters, idle)
from Python_ARQ import ARQ
from config import *


print("[INFO]: INITIALIZING BOT CLIENT ...")
luna = Client(":memory:",
              bot_token=bot_token,
              api_id=api_id,
              api_hash=api_hash,
)
bot_id = int(bot_token.split(":")[0])
print("[INFO]: INITIALIZING ...")
arq = None


START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ('week', 60 * 60 * 24 * 7),
    ('day', 60 * 60 * 24),
    ('hour', 60 * 60),
    ('min', 60),
    ('sec', 1)
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return 'inf'
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append('{} {}{}'
                         .format(amount, unit, "" if amount == 1 else "s"))
    return ', '.join(parts)


async def lunaQuery(query: str, user_id: int):
    query = (
        query
        if LANGUAGE == "en"
        else (await arq.translate(query, "en")).result.translatedText
    )
    resp = (await arq.luna(query, user_id)).result
    return (
        resp
        if LANGUAGE == "en"
        else (
            await arq.translate(resp, LANGUAGE)
        ).result.translatedText
    )


async def type_and_send(message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else 0
    query = message.text.strip()
    await message._client.send_chat_action(chat_id, "typing")
    response, _ = await gather(lunaQuery(query, user_id), sleep(2))
    if "Luna" in response:
        responsee = response.replace("Luna", "skyzu")
    else:
        responsee = response
    if "Aco" in responsee:
        responsess = responsee.replace("Aco", "skyzu")
    else:
        responsess = responsee
    if "siapa ultra?" in responsess:
        responsess2 = responsess.replace("siapa skyzu?", "What?👀")
    else:
        responsess2 = responsess
    await message.reply_text(responsess2)
    await message._client.send_chat_action(chat_id, "cancel")

@luna.on_message(
    ~filters.private
    & filters.text
    & ~filters.command(["start", "start@skyzumusicbot"])
    & ~filters.edited,
    group=69,
)
async def chat(_, message):
    if message.reply_to_message:
        if not message.reply_to_message.from_user:
            return
        from_user_id = message.reply_to_message.from_user.id
        if from_user_id != bot_id:
            return
    else:
        match = re.search(
            "[.|\n]{0,}skyzu[.|\n]{0,}",
            message.text.strip(),
            flags=re.IGNORECASE,
        )
        if not match:
            return
    await type_and_send(message)


@luna.on_message(
    filters.private
    & ~filters.command(["start", "start@skyzumusicbot"])
    & ~filters.edited
)
async def chatpm(_, message):
    if not message.text:
        await message.reply_text("Ufff... ignoring ....")
        return
    await type_and_send(message)


async def main():
    global arq
    session = ClientSession()
    arq = ARQ(ARQ_API_BASE_URL, ARQ_API_KEY, session)

    await luna.start()
    print(
        """
    -----------------
  | Chatbot Started! |
    -----------------
"""
    )
    await idle()


loop = get_event_loop()
loop.run_until_complete(main())
