import logging
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = "8824069105:AAHM27eSHoC5ytMuLxS5DrKB1ZCciauRYTc”

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
def is_valid_url(text):
    return any(domain in text for domain in [
        "youtube.com", "youtu.be",
        "instagram.com",
        "tiktok.com", "vm.tiktok.com"
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men Dostonjn Music botman!\n\n"
        "Quyidagilarni qila olaman:\n"
        "YouTube, Instagram, TikTok havolasini yuboring\n"
        "Men video yoki MP3 yuboraman\n\n"
        "/audio - faqat MP3\n"
        "/video - video"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Yordam:\n\n"
        "Havola yuboring - video yuklayman\n"
        "/audio - MP3 yuklayman\n"
        "/video - video yuklayman"
    )
def download_video(url, audio_only=False):
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
            title = info.get("title", "Unknown")
            uploader = info.get("uploader", info.get("channel", "Unknown"))
            if audio_only:
                filename = ydl.prepare_filename(info)
                base = os.path.splitext(filename)[0]
                file_path = base + ".mp3"
            else:
                file_path = ydl.prepare_filename(info)
            result.update({"success": True, "file": file_path, "title": title, "uploader": uploader})
    except Exception as e:
        result["error"] = str(e)

    return result
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
    caption = f"🎵 <b>{title}</b>\n👤 {uploader}"

    try:
        await msg.edit_text("📤 Yuborilmoqda...")
        if audio_only:
            with open(file_path, "rb") as f:
                await update.message.reply_audio(
                    audio=f,
                    caption=caption,
                    parse_mode="HTML",
                    title=title,
                    performer=uploader
                )
        else:
            with open(file_path, "rb") as f:
                await update.message.reply_video(
                    video=f,
                    caption=caption,
                    parse_mode="HTML"
                )
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"❌ Yuborishda xatolik: {str(e)}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
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
