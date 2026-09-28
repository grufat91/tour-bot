#!/usr/bin/env python3
"""
Tour Bot - Telegram → WhatsApp
Satıcılar: Telegram Kanalına tur yazır (+150 AZN otomatik əlavə)
Müştərilər: WhatsApp Kanalında görür
"""

from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import logging
import re

# Config
TOKEN = "8911797784:AAH12z6PnSdqCX6pi_50s66EAt YhLMRcEN4"
TELEGRAM_CHANNEL = -1003303207925
MARKUP_AZN = 150

# Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Telegram mesajını oxu:
    1. Qiyməti tap
    2. +150 AZN əlavə et
    3. Premium template-ə doldur
    4. Geri göndər
    """

    try:
        msg_text = update.message.text

        # Qiymət tap (nümunə: "2480 AZN" → 2480)
        price_match = re.search(r'(\d+)\s*(?:AZN|₼)', msg_text)
        original_price = int(price_match.group(1)) if price_match else 0
        new_price = original_price + MARKUP_AZN if original_price > 0 else 0

        # Premium Template
        formatted_msg = f"""
✈️ TUR PAKET

{msg_text}

━━━━━━━━━━━━━━━━
💰 SƏN'İN QİYMƏTİ: {new_price} AZN
   (+{MARKUP_AZN} AZN kommissiya əlavə edildi)
━━━━━━━━━━━━━━━━

📞 SİFARİŞ ET:
+994 50 XXX XX XX (WhatsApp)

✅ Həmişə ən yaxşı qiymətlər!
"""

        # Mesajı göndər
        await context.bot.send_message(
            chat_id=TELEGRAM_CHANNEL,
            text=formatted_msg,
            parse_mode="HTML"
        )

        # Satıcıya cavab
        await update.message.reply_text(
            f"✅ Tur qəbul edildi!\n\n"
            f"Orijinal: {original_price} AZN\n"
            f"Yeni: {new_price} AZN\n\n"
            f"Müştərilərə göndərilir..."
        )

        logger.info(f"Tour processed: {original_price} → {new_price} AZN")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await update.message.reply_text(f"❌ Xəta: {str(e)}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text(
        "🤖 Tour Bot Aktiv!\n\n"
        "Turlarınızı yazın, mən otomatik olaraq:\n"
        "✅ Qiymətə +150 AZN əlavə edəcəyəm\n"
        "✅ Template-ə dolduracağam\n"
        "✅ Müştərilərə göndərəcəyəm"
    )


def main():
    """Bot start"""
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start
    logger.info("Bot başladı...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
