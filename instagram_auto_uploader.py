
import os, time, shutil, asyncio
from telegram import Application, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from instagrapi import Client
import google.generativeai as genai

BOT_TOKEN = "8027728156:AAEU3dfD4Bf9POmwGWtfRVbFUwrZqCh7x_A"
INSTAGRAM_USERNAME = "anay_a.3"
INSTAGRAM_PASSWORD = "kartik+1234"
GEMINI_API_KEY = "AIzaSyBfJrDsz0TDvWWMt9mxG-qwTB9xlUhbDf0"
OWNER_TELEGRAM_ID = 7943866981

REELS_FOLDER = "reels_queue"
UPLOADED_FOLDER = "uploaded"
os.makedirs(REELS_FOLDER, exist_ok=True)
os.makedirs(UPLOADED_FOLDER, exist_ok=True)

genai.configure(api_key=GEMINI_API_KEY)

async def generate_caption():
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content("Write a short, trendy Instagram reel caption with 2 hashtags.")
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini error:", e)
        return "🔥 Auto-posted! #reels #trending"

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.video:
        return
    video_file = await message.video.get_file()
    file_name = f"{int(time.time())}.mp4"
    file_path = os.path.join(REELS_FOLDER, file_name)
    await video_file.download_to_drive(file_path)
    print(f"📥 Saved video to queue: {file_name}")

async def upload_next_reel():
    files = sorted(os.listdir(REELS_FOLDER))
    if not files:
        await send_telegram_message("Boss, I am waiting for your orders 😎")
        return
    filename = files[0]
    filepath = os.path.join(REELS_FOLDER, filename)
    caption = await generate_caption()
    try:
        cl = Client()
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.clip_upload(filepath, caption)
        shutil.move(filepath, os.path.join(UPLOADED_FOLDER, filename))
        print(f"✅ Uploaded to Instagram: {filename}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

async def send_telegram_message(message):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=OWNER_TELEGRAM_ID, text=message)

async def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(upload_next_reel()), "interval", hours=10)
    scheduler.start()
    print("🤖 Bot is live... send videos to forward.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(run_bot())
