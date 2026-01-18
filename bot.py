"""
Telegram Bot for generating text images.
Users send 2 lines of text and receive a PNG image.
"""

import os
import io
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from image_generator import generate_text_image

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    welcome_message = """สวัสดีครับ! ยินดีต้อนรับสู่ Text Image Bot

วิธีใช้งาน:
ส่งข้อความ 2 บรรทัด แล้วบอทจะสร้างรูปภาพให้

ตัวอย่าง:
ฟองสบู่จัดเต็ม
เหมือนอยู่ในฝัน!

บรรทัดแรก = สีส้ม
บรรทัดที่สอง = สีขาว
"""
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = """คำสั่งที่ใช้ได้:
/start - เริ่มต้นใช้งาน
/help - แสดงวิธีใช้

ส่งข้อความ 2 บรรทัดเพื่อสร้างรูปภาพ
บรรทัดแรก = ข้อความสีส้ม
บรรทัดที่สอง = ข้อความสีขาว
"""
    await update.message.reply_text(help_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages."""
    text = update.message.text.strip()
    lines = text.split('\n')

    # Check if we have exactly 2 lines
    if len(lines) < 2:
        await update.message.reply_text(
            "กรุณาส่งข้อความ 2 บรรทัด\n\nตัวอย่าง:\nฟองสบู่จัดเต็ม\nเหมือนอยู่ในฝัน!"
        )
        return

    # Take first 2 lines
    line1 = lines[0].strip()
    line2 = lines[1].strip()

    if not line1 or not line2:
        await update.message.reply_text("ทั้งสองบรรทัดต้องมีข้อความ")
        return

    # Send "generating" message
    processing_msg = await update.message.reply_text("กำลังสร้างรูปภาพ...")

    try:
        # Generate the image
        image_bytes = generate_text_image(line1, line2)

        # Send as document to preserve PNG transparency
        image_file = io.BytesIO(image_bytes)
        image_file.name = "text_image.png"
        await update.message.reply_document(
            document=image_file,
            caption=f"{line1}\n{line2}"
        )

        # Delete the processing message
        await processing_msg.delete()

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        await processing_msg.edit_text(f"เกิดข้อผิดพลาด: {str(e)}")


def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with TELEGRAM_BOT_TOKEN=your_token")
        return

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
