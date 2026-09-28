#!/usr/bin/env python3
"""
Tour Bot
- Bota (şəxsi çatda) tur mətni/şəkli göndər -> qiymətə +MARKUP əlavə edib hazır postu qaytarır
- Kanalda post olsa -> formatlanmış versiyanı kanala atır, orijinalı silir
Token kodda YOXDUR - Render Environment-də BOT_TOKEN kimi saxlanılır.
"""

import logging
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.environ["BOT_TOKEN"]
MARKUP_AZN = int(os.environ.get("MARKUP_AZN", "150"))
WHATSAPP = os.environ.get("WHATSAPP_NUMBER", "+994 50 XXX XX XX")

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("tour-bot")

# "1500 AZN", "1 500 ₼", "1.500 azn", "2480manat"
PRICE_RE = re.compile(
    r"(?<![\d.,])(\d{1,3}(?:[ .,]\d{3})+|\d+)\s*(AZN|₼|manat)",
    re.IGNORECASE,
)


def add_markup(text: str):
    """Mətndəki bütün AZN qiymətlərinə MARKUP əlavə edir."""
    changes = []

    def repl(m):
        old = int(re.sub(r"\D", "", m.group(1)))
        new = old + MARKUP_AZN
        changes.append((old, new))
        return f"{new} {m.group(2)}"

    return PRICE_RE.sub(repl, text), changes


BRAND = os.environ.get("BRAND_NAME", "RR TOURS")

# Satıcının əlaqə məlumatı olan sətirlər silinir (müştəri birbaşa ona getməsin)
CONTACT_RE = re.compile(
    r"(\+?\d[\d\s\-()]{8,}\d|https?://|t\.me/|wa\.me/|@\w{3,}|whatsapp|əlaqə|elaqe|zəng|zeng|\btel[:.]|nömrə|nomre)",
    re.IGNORECASE,
)


def clean_text(text: str) -> str:
    lines = [l for l in text.splitlines() if not CONTACT_RE.search(l)]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def build_post(text: str, changes) -> str:
    body = clean_text(text)
    main_price = changes[0][1]
    price_line = f"{main_price} AZN" + ("-dən başlayaraq" if len(changes) > 1 else "")
    return (
        f"🌍 *{BRAND}* 🌍\n"
        "✨ *ÖZƏL TUR TƏKLİFİ* ✨\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{body}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"💎 *QİYMƏT: {price_line}*\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"📲 *Sifariş:* {WHATSAPP}\n"
        "⏳ Yerlər məhduddur — tələsin!\n"
        "🛡️ Rəsmi rezervasiya · Etibarlı xidmət"
    )


async def send_post(context, chat_id, msg, post):
    """Şəkil varsa şəkil + caption, yoxdursa mətn göndərir."""
    if msg.photo and len(post) <= 1024:
        await context.bot.send_photo(chat_id, msg.photo[-1].file_id, caption=post)
    else:
        if msg.photo:
            await context.bot.send_photo(chat_id, msg.photo[-1].file_id)
        await context.bot.send_message(chat_id, post)


async def private_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    text = msg.text or msg.caption or ""
    new_text, changes = add_markup(text)

    if not changes:
        await msg.reply_text("⚠️ Qiymət tapılmadı. Mətndə məs. '1500 AZN' olmalıdır.")
        return

    await send_post(context, msg.chat_id, msg, build_post(new_text, changes))
    summary = ", ".join(f"{o} → {n}" for o, n in changes)
    await msg.reply_text(f"✅ Hazırdır ({summary} AZN). Yuxarıdakını WhatsApp-a forward et.")
    log.info("private: %s", summary)


async def channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    text = msg.text or msg.caption or ""
    new_text, changes = add_markup(text)
    if not changes:
        return  # qiymətsiz postlara toxunmuruq

    await send_post(context, msg.chat_id, msg, build_post(new_text, changes))
    try:
        await msg.delete()
    except Exception as e:
        log.warning("orijinal silinmədi: %s", e)
    log.info("channel: %s", changes)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        f"🤖 Tour Bot aktivdir!\n\nTur mətnini (və ya şəkil+mətn) göndər — "
        f"qiymətə +{MARKUP_AZN} AZN əlavə edib hazır post qaytaracağam."
    )


class Health(BaseHTTPRequestHandler):
    """Render Web Service port tələb edir + ping üçün."""

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):
        pass


def run_health_server():
    port = int(os.environ.get("PORT", "10000"))
    HTTPServer(("0.0.0.0", port), Health).serve_forever()


def main():
    threading.Thread(target=run_health_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & (filters.TEXT | filters.PHOTO) & ~filters.COMMAND,
            private_handler,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.UpdateType.CHANNEL_POSTS & (filters.TEXT | filters.PHOTO),
            channel_handler,
        )
    )

    log.info("Bot başladı...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
