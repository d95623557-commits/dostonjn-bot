import logging
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = 8317767665:AAE8f3XQ3Fyqyfy0Bep2As88Bll0hdHSDzw

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
def is_valid_url(text: str) -> bool:
    return any(domain in text for domain in [
        "youtube.com", "youtu.be",
        "instagram.com",
        "tiktok.com", "vm.tiktok.com"
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Men video/musiqa yuklab beruvchi botman.\n\n"
        "📌 Ishlatish:\n"
        "• YouTube, Instagram yoki TikTok havolasini yuboring\n"
        "• Men videoni yoki musiqa faylini yuboraman\n\n"
        "🎵 /audio — faqat musiqa (MP3)\n"
        "🎬 /video — video yuklab olish\n\n"
        "Havola yuboring! 🚀"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Yordam:\n\n"
        "1️⃣ Havola yuboring\n"
        "2️⃣ Bot videoni yoki MP3 yuboradi\n\n"
        "/start — Boshlash\n"
        "/audio [havola] — MP3 audio\n"
        "/video [havola] — Video"
    )
def download_video(url: str, audio_only: bool = False) -> dict:
    result = {"success": False, "file": None, "title": "", "uploader": "", "error": ""}

    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }

    if audio_only:
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        ydl_opts.update({
            "format": "best[filesize<45M]/best[height<=720]/best",
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "
 async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE, audio_only: bool = False):
    text = update.message.text.strip()

    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await update.message.reply_text("⚠️ Havola kiriting!\nMisol: /audio https://youtube.com/...")
            return
        url = parts[1].strip()
    else:
        url = text

    if not is_valid_url(url):
        await update.message.reply_text(
            "❌ Noto'g'ri havola!\n"
            "YouTube, Instagram yoki TikTok havolasini yuboring."
        )
        return

    msg = await update.message.reply_text("⏳ Yuklanmoqda... Biroz kuting.")

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, download_video, url, audio_only)

    if not result["success"]:
        await msg.edit_text(
            f"❌ Xatolik:\n{result['error']}\n\nQayta urinib ko'ring."
        )
        return

    file_path = result["file"]
    title = result["title"]
    uploader = result["uploader"]
    caption = f"🎵 
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_url(update, context, audio_only=False)


async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_url(update, context, audio_only=True)


async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_url(update, context, audio_only=False)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("audio", audio_command))
    app.add_handler(CommandHandler("video", video_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("✅ Bot ishga tushdi!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
